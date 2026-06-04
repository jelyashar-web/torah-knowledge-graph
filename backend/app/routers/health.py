"""Health check endpoint with deep service probes."""

import asyncio
import time

import structlog
from fastapi import APIRouter

from app.config import settings
from app.neo4j_client import check_health as neo4j_health
from app.qdrant_client import check_health as qdrant_health

logger = structlog.get_logger()
router = APIRouter(tags=["health"])


async def _postgres_health() -> dict:
    from app.db import engine
    from sqlalchemy import text
    start = time.time()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "latency_ms": round((time.time() - start) * 1000, 2)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def _redis_health() -> dict:
    import redis.asyncio as aioredis
    start = time.time()
    try:
        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        await r.close()
        return {"status": "ok", "latency_ms": round((time.time() - start) * 1000, 2)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/health")
async def health_check():
    neo4j, postgres, qdrant, redis = await asyncio.gather(
        neo4j_health(),
        _postgres_health(),
        qdrant_health(),
        _redis_health(),
    )

    all_ok = all(
        s["status"] == "ok" for s in [neo4j, postgres, qdrant, redis]
    )

    return {
        "status": "healthy" if all_ok else "degraded",
        "services": {
            "neo4j": neo4j,
            "postgres": postgres,
            "qdrant": qdrant,
            "redis": redis,
        },
    }
