"""Torah Embeddings Service — semantic vector generation for Jewish texts.

Supports multiple providers:
- Ollama (local): nomic-embed-text, mxbai-embed-large
- SentenceTransformers (local): multilingual-e5, LaBSE
- OpenAI (cloud): text-embedding-3-large
- Kimi (cloud): via OpenAI-compatible API

All embeddings are normalized L2 for cosine similarity.
"""

import asyncio
import hashlib
import json
import structlog
import numpy as np
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

logger = structlog.get_logger()


@dataclass
class EmbeddingResult:
    text: str
    vector: List[float]
    model: str
    provider: str
    dimension: int
    normalized: bool = True
    elapsed_ms: float = 0.0
    cached: bool = False


class TorahEmbeddingService:
    """Unified embedding service with caching and provider fallback."""

    SUPPORTED_PROVIDERS = ["ollama", "sentence_transformers", "openai", "kimi"]

    # Model configs per provider
    MODELS = {
        "ollama": {
            "default": "nomic-embed-text",
            "torah": "mxbai-embed-large",  # Best for multilingual
            "url": "http://localhost:11434/api/embeddings",
        },
        "sentence_transformers": {
            "default": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "torah": "BAAI/bge-m3",  # Multilingual, 8192 context
            "hebrew": "imvladikon/sentence-transformers-alephbert",
        },
        "openai": {
            "default": "text-embedding-3-small",
            "torah": "text-embedding-3-large",
        },
        "kimi": {
            "default": "kimi-embedding",
            "url": "https://api.moonshot.cn/v1/embeddings",
        },
    }

    def __init__(
        self,
        provider: str = "ollama",
        model: Optional[str] = None,
        cache_enabled: bool = True,
    ):
        self.provider = provider
        self.model = model or self.MODELS[provider]["default"]
        self.cache_enabled = cache_enabled
        self._cache: Dict[str, EmbeddingResult] = {}
        self._st_model = None  # Lazy load for sentence-transformers
        self._dimension = self._detect_dimension()

        logger.info(
            "embeddings_service_init",
            provider=provider,
            model=self.model,
            dimension=self._dimension,
        )

    def _detect_dimension(self) -> int:
        """Auto-detect embedding dimension based on model."""
        dims = {
            "nomic-embed-text": 768,
            "mxbai-embed-large": 1024,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "paraphrase-multilingual-MiniLM-L12-v2": 384,
            "BAAI/bge-m3": 1024,
            "kimi-embedding": 2048,
        }
        return dims.get(self.model, 768)

    def _make_cache_key(self, text: str) -> str:
        """Deterministic cache key."""
        content = f"{self.provider}:{self.model}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _normalize(self, vector: List[float]) -> List[float]:
        """L2 normalize a vector."""
        arr = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(arr)
        if norm == 0:
            return arr.tolist()
        return (arr / norm).tolist()

    async def _embed_ollama(self, text: str) -> EmbeddingResult:
        """Generate embedding via Ollama API."""
        import httpx
        import time as time_module

        start = time_module.time()
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(
                self.MODELS["ollama"]["url"],
                json={"model": self.model, "prompt": text},
            )
            res.raise_for_status()
            data = res.json()
            vector = self._normalize(data["embedding"])
            elapsed = (time_module.time() - start) * 1000

            return EmbeddingResult(
                text=text,
                vector=vector,
                model=self.model,
                provider="ollama",
                dimension=len(vector),
                elapsed_ms=elapsed,
            )

    async def _embed_sentence_transformers(self, text: str) -> EmbeddingResult:
        """Generate embedding via sentence-transformers (local)."""
        import time as time_module

        if self._st_model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("loading_sentence_transformer", model=self.model)
            self._st_model = SentenceTransformer(self.model)

        start = time_module.time()
        # Run in thread pool since ST is synchronous
        loop = asyncio.get_event_loop()
        vector = await loop.run_in_executor(
            None, lambda: self._st_model.encode(text, normalize_embeddings=True)
        )
        elapsed = (time_module.time() - start) * 1000

        return EmbeddingResult(
            text=text,
            vector=vector.tolist(),
            model=self.model,
            provider="sentence_transformers",
            dimension=len(vector),
            elapsed_ms=elapsed,
        )

    async def _embed_openai(self, text: str) -> EmbeddingResult:
        """Generate embedding via OpenAI API."""
        import time as time_module
        import httpx

        start = time_module.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self._get_api_key('openai')}",
                    "Content-Type": "application/json",
                },
                json={"model": self.model, "input": text},
            )
            res.raise_for_status()
            data = res.json()
            vector = self._normalize(data["data"][0]["embedding"])
            elapsed = (time_module.time() - start) * 1000

            return EmbeddingResult(
                text=text,
                vector=vector,
                model=self.model,
                provider="openai",
                dimension=len(vector),
                elapsed_ms=elapsed,
            )

    async def _embed_kimi(self, text: str) -> EmbeddingResult:
        """Generate embedding via Kimi API."""
        import time as time_module
        import httpx

        start = time_module.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                "https://api.moonshot.cn/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self._get_api_key('kimi')}",
                    "Content-Type": "application/json",
                },
                json={"model": self.model, "input": text},
            )
            res.raise_for_status()
            data = res.json()
            vector = self._normalize(data["data"][0]["embedding"])
            elapsed = (time_module.time() - start) * 1000

            return EmbeddingResult(
                text=text,
                vector=vector,
                model=self.model,
                provider="kimi",
                dimension=len(vector),
                elapsed_ms=elapsed,
            )

    def _get_api_key(self, provider: str) -> str:
        """Get API key from environment."""
        import os

        keys = {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "kimi": os.getenv("KIMI_API_KEY", ""),
        }
        return keys.get(provider, "")

    async def embed(self, text: str) -> EmbeddingResult:
        """Generate embedding with caching and fallback."""
        # Check cache
        if self.cache_enabled:
            cache_key = self._make_cache_key(text)
            if cache_key in self._cache:
                cached = self._cache[cache_key]
                cached.cached = True
                return cached

        # Generate embedding
        embedders = {
            "ollama": self._embed_ollama,
            "sentence_transformers": self._embed_sentence_transformers,
            "openai": self._embed_openai,
            "kimi": self._embed_kimi,
        }

        embedder = embedders.get(self.provider)
        if not embedder:
            raise ValueError(f"Unknown provider: {self.provider}")

        try:
            result = await embedder(text)
        except Exception as e:
            logger.error(
                "embedding_failed",
                provider=self.provider,
                model=self.model,
                error=str(e),
            )
            raise

        # Cache result
        if self.cache_enabled:
            self._cache[self._make_cache_key(text)] = result

        return result

    async def embed_batch(
        self, texts: List[str], batch_size: int = 32, progress_callback: Optional[Callable] = None
    ) -> List[EmbeddingResult]:
        """Batch embedding with progress tracking."""
        results = []
        total = len(texts)

        for i in range(0, total, batch_size):
            batch = texts[i : i + batch_size]
            batch_results = await asyncio.gather(
                *[self.embed(text) for text in batch],
                return_exceptions=True,
            )

            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(
                        "batch_embedding_failed",
                        text=batch[j][:50],
                        error=str(result),
                    )
                    # Return zero vector as fallback
                    results.append(
                        EmbeddingResult(
                            text=batch[j],
                            vector=[0.0] * self._dimension,
                            model=self.model,
                            provider=self.provider,
                            dimension=self._dimension,
                        )
                    )
                else:
                    results.append(result)

            if progress_callback:
                progress_callback(min(i + batch_size, total), total)

        return results

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two normalized vectors."""
        return float(np.dot(np.array(a), np.array(b)))

    def clear_cache(self):
        """Clear the embedding cache."""
        self._cache.clear()
        logger.info("embedding_cache_cleared")


# ── Qdrant Integration ──────────────────────────────────

class TorahVectorStore:
    """Store and search Torah embeddings in Qdrant."""

    def __init__(self, collection_name: str = "torah_embeddings"):
        from app.qdrant_client import qdrant_client

        self.client = qdrant_client.client
        self.collection = collection_name
        self.embedding_service = TorahEmbeddingService()

    def _ensure_collection(self, dimension: int = 768):
        """Create collection if it doesn't exist."""
        from qdrant_client.models import Distance, VectorParams

        try:
            self.client.get_collection(self.collection)
        except Exception:
            logger.info("creating_qdrant_collection", name=self.collection, dimension=dimension)
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
            )

    async def index_verse(
        self, ref: str, hebrew: str, english: Optional[str] = None, metadata: Optional[Dict] = None
    ):
        """Index a single verse into Qdrant."""
        from qdrant_client.models import PointStruct

        # Use Hebrew text as primary embedding source
        text = hebrew or english or ref
        embedding = await self.embedding_service.embed(text)

        self._ensure_collection(embedding.dimension)

        point_id = hashlib.sha256(ref.encode()).hexdigest()
        payload = {
            "ref": ref,
            "hebrew": hebrew,
            "english": english,
            "type": "verse",
            **(metadata or {}),
        }

        self.client.upsert(
            collection_name=self.collection,
            points=[PointStruct(id=point_id, vector=embedding.vector, payload=payload)],
        )

        logger.info("verse_indexed", ref=ref, dimension=embedding.dimension)

    async def index_verses_batch(
        self, verses: List[Dict], progress_callback: Optional[Callable] = None
    ):
        """Batch index verses."""
        from qdrant_client.models import PointStruct

        texts = [v.get("hebrew", v.get("english", v["ref"])) for v in verses]
        embeddings = await self.embedding_service.embed_batch(
            texts, progress_callback=progress_callback
        )

        dimension = embeddings[0].dimension if embeddings else 768
        self._ensure_collection(dimension)

        points = []
        for verse, emb in zip(verses, embeddings):
            point_id = hashlib.sha256(verse["ref"].encode()).hexdigest()
            payload = {
                "ref": verse["ref"],
                "hebrew": verse.get("hebrew"),
                "english": verse.get("english"),
                "book": verse.get("book"),
                "chapter": verse.get("chapter"),
                "verse": verse.get("verse"),
                "type": "verse",
            }
            points.append(PointStruct(id=point_id, vector=emb.vector, payload=payload))

        # Upsert in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            self.client.upsert(
                collection_name=self.collection,
                points=points[i : i + batch_size],
            )

        logger.info("verses_batch_indexed", count=len(verses))

    async def search(self, query: str, limit: int = 10, filters: Optional[Dict] = None) -> List[Dict]:
        """Semantic search via Qdrant."""
        from qdrant_client.models import Filter

        embedding = await self.embedding_service.embed(query)

        search_filter = Filter(**filters) if filters else None

        results = self.client.search(
            collection_name=self.collection,
            query_vector=embedding.vector,
            limit=limit,
            query_filter=search_filter,
            with_payload=True,
        )

        return [
            {
                "score": r.score,
                "ref": r.payload.get("ref"),
                "hebrew": r.payload.get("hebrew"),
                "english": r.payload.get("english"),
                "book": r.payload.get("book"),
                "metadata": {k: v for k, v in r.payload.items() if k not in ["ref", "hebrew", "english", "book"]},
            }
            for r in results
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        try:
            info = self.client.get_collection(self.collection)
            return {
                "collection": self.collection,
                "vectors_count": info.points_count,
                "dimension": info.config.params.vectors.size,
                "distance": str(info.config.params.vectors.distance),
                "model": self.embedding_service.model,
                "provider": self.embedding_service.provider,
            }
        except Exception as e:
            return {"error": str(e)}


# ── Global instances ────────────────────────────────────

embedding_service = TorahEmbeddingService()
vector_store = TorahVectorStore()
