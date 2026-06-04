"""Qdrant vector database client and collection management."""

import structlog
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config import settings

logger = structlog.get_logger()

_client = None

COLLECTION_NAME = "torah_verses"


async def get_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
    return _client


async def init_collection():
    """Create collection if it does not exist."""
    client = await get_client()
    try:
        collections = await client.get_collections()
        existing = [c.name for c in collections.collections]
        if COLLECTION_NAME in existing:
            logger.info("qdrant_collection_exists", collection=COLLECTION_NAME)
            return

        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=settings.embedding_dimensions,
                distance=Distance.COSINE,
            ),
        )
        logger.info("qdrant_collection_created", collection=COLLECTION_NAME)
    except Exception as e:
        logger.error("qdrant_collection_init_failed", error=str(e))
        raise


async def check_health() -> dict:
    try:
        client = await get_client()
        await client.get_collections()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
