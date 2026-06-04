"""FastAPI application entry point."""

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_prometheus import metrics, PrometheusMiddleware
from strawberry.fastapi import GraphQLRouter

# Ensure Celery app is configured before importing tasks
from app.celery_app import celery_app  # noqa: F401
from app.config import settings
from app.neo4j_client import init_schema as init_neo4j_schema
from app.qdrant_client import init_collection as init_qdrant_collection
from app.routers import discover, graph, health, ingest, search
from app.graphql.schema import schema

logger = structlog.get_logger()

app = FastAPI(
    title="Torah Knowledge Graph API",
    description="Graph-native knowledge platform for Torah literature",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware
app.add_middleware(PrometheusMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.add_route("/metrics", metrics)
app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(graph.router)
app.include_router(discover.router)

# GraphQL
graphql_router = GraphQLRouter(
    schema,
    path="/graphql",
    graphiql=True,
    allow_queries_via_get=True,
)
app.include_router(graphql_router, prefix="/graphql")


@app.on_event("startup")
async def startup():
    logger.info("backend_startup", environment=settings.environment)
    try:
        await init_neo4j_schema()
    except Exception as e:
        logger.error("neo4j_schema_init_failed", error=str(e))
    try:
        await init_qdrant_collection()
    except Exception as e:
        logger.error("qdrant_collection_init_failed", error=str(e))


@app.on_event("shutdown")
async def shutdown():
    from app.neo4j_client import close_driver
    await close_driver()
    logger.info("backend_shutdown")
