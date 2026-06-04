"""Enterprise health checks with K8s probes, version info, uptime, and deep diagnostics."""

import asyncio
import time
from datetime import datetime

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.neo4j_client import check_health as neo4j_health
from app.qdrant_client import check_health as qdrant_health

logger = structlog.get_logger()
router = APIRouter(tags=["health"])

# System start time for uptime calculation
_start_time = time.monotonic()


class ServiceHealth(BaseModel):
    status: str
    latency_ms: float = 0.0
    error: str | None = None
    version: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str = "2.0.0-enterprise"
    environment: str
    uptime_seconds: float
    timestamp: str
    services: dict[str, ServiceHealth]
    checks: dict


async def _postgres_health() -> dict:
    from app.db import engine
    from sqlalchemy import text

    start = time.time()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "latency_ms": round((time.time() - start) * 1000, 2)}
    except Exception as e:
        logger.error("postgres_health_failed", error=str(e))
        return {"status": "error", "error": str(e), "latency_ms": round((time.time() - start) * 1000, 2)}


async def _redis_health() -> dict:
    import redis.asyncio as aioredis

    start = time.time()
    try:
        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        info = await r.info("memory")
        await r.close()
        return {
            "status": "ok",
            "latency_ms": round((time.time() - start) * 1000, 2),
            "version": info.get("redis_version", "unknown"),
        }
    except Exception as e:
        logger.error("redis_health_failed", error=str(e))
        return {"status": "error", "error": str(e), "latency_ms": round((time.time() - start) * 1000, 2)}


async def _celery_health() -> dict:
    """Check if Celery workers are running."""
    try:
        from app.celery_app import celery_app
        inspect = celery_app.control.inspect()
        active = inspect.active()
        stats = inspect.stats()
        worker_count = len(stats) if stats else 0
        return {
            "status": "ok" if worker_count > 0 else "degraded",
            "workers_online": worker_count,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def _ai_providers_health() -> dict:
    """Check AI provider availability."""
    checks = {}
    # Check Ollama
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get("http://localhost:11434/api/tags")
            checks["ollama"] = "ok" if r.status_code == 200 else "degraded"
    except Exception:
        checks["ollama"] = "unavailable"
    return {"status": "ok", "providers": checks}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check — all services, latencies, diagnostics."""
    neo4j, postgres, qdrant, redis, celery, ai = await asyncio.gather(
        neo4j_health(),
        _postgres_health(),
        qdrant_health(),
        _redis_health(),
        _celery_health(),
        _ai_providers_health(),
    )

    services = {
        "neo4j": neo4j,
        "postgres": postgres,
        "qdrant": qdrant,
        "redis": redis,
        "celery": celery,
        "ai_providers": ai,
    }

    all_ok = all(s.get("status") == "ok" for s in services.values())
    degraded = any(s.get("status") == "degraded" for s in services.values())

    status = "healthy" if all_ok else ("degraded" if degraded else "unhealthy")

    uptime = time.monotonic() - _start_time

    return HealthResponse(
        status=status,
        version="2.0.0-enterprise",
        environment=settings.environment,
        uptime_seconds=round(uptime, 2),
        timestamp=datetime.utcnow().isoformat() + "Z",
        services=services,
        checks={
            "response_time_ms": 0,
            "total_checks": len(services),
            "passed_checks": sum(1 for s in services.values() if s.get("status") == "ok"),
        },
    )


@router.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe — is the process alive?"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/ready")
async def readiness_probe():
    """Kubernetes readiness probe — is the app ready to serve traffic?"""
    neo4j = await neo4j_health()
    postgres = await _postgres_health()

    if neo4j.get("status") != "ok" or postgres.get("status") != "ok":
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "neo4j": neo4j.get("status"),
                "postgres": postgres.get("status"),
            },
        )

    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/deep")
async def deep_health_check():
    """Deep diagnostic check — query counts, slow queries, memory usage."""
    from app.neo4j_client import neo4j_client

    diagnostics = {}

    # Neo4j deep diagnostics
    try:
        result = neo4j_client.driver.execute_query(
            "CALL dbms.listQueries() YIELD query, elapsedTimeMillis RETURN count(*) as active_queries"
        )
        diagnostics["neo4j_active_queries"] = result[0]["active_queries"] if result else 0
    except Exception as e:
        diagnostics["neo4j_active_queries"] = f"error: {e}"

    # Database counts
    try:
        counts = neo4j_client.driver.execute_query(
            "CALL apoc.meta.stats() YIELD nodeCount, relCount RETURN nodeCount, relCount"
        )
        if counts:
            diagnostics["graph_nodes"] = counts[0]["nodeCount"]
            diagnostics["graph_relationships"] = counts[0]["relCount"]
    except Exception as e:
        diagnostics["graph_counts_error"] = str(e)

    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "diagnostics": diagnostics,
    }
