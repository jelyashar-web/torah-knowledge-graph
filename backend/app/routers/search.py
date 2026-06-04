"""Search API: fulltext, semantic, hybrid — unified search with Torah embeddings."""

from typing import Any, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.config import settings
from app.neo4j_client import get_driver
from app.embeddings import TorahEmbeddingService, TorahVectorStore

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/search", tags=["search"])

# Global services (lazy init)
_vector_store: Optional[TorahVectorStore] = None
_embedding_service: Optional[TorahEmbeddingService] = None


def get_vector_store() -> TorahVectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = TorahVectorStore()
    return _vector_store


def get_embedding_service() -> TorahEmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = TorahEmbeddingService()
    return _embedding_service


# ── Fulltext Search ─────────────────────────────────────

@router.get("/fulltext")
async def fulltext_search(
    q: str = Query(..., min_length=1, max_length=200),
    book: str | None = None,
    limit: int = Query(default=20, le=100),
):
    """Fulltext search via Neo4j full-text index."""
    driver = await get_driver()
    async with driver.session() as session:
        # Use Neo4j full-text index
        cypher = """
        CALL db.index.fulltext.queryNodes('verseHebrewText', $search_query) YIELD node, score
        """
        if book:
            cypher += " WHERE node.book = $book"
        cypher += " RETURN node {.*} AS verse, score LIMIT $limit"

        result = await session.run(cypher, search_query=q, book=book, limit=limit)
        records = [record.data() async for record in result]

    return {"query": q, "results": records, "count": len(records), "type": "fulltext"}


# ── Semantic Search ────────────────────────────────────

@router.get("/semantic")
async def semantic_search(
    q: str = Query(..., min_length=1, max_length=200),
    book: str | None = None,
    limit: int = Query(default=20, le=100),
):
    """Semantic search via Qdrant vector similarity using Torah embeddings."""
    try:
        store = get_vector_store()
        filters = None
        if book:
            from qdrant_client.models import FieldCondition, MatchValue
            filters = {
                "must": [FieldCondition(key="book", match=MatchValue(value=book))]
            }

        results = await store.search(q, limit=limit, filters=filters)

        # Enrich with Neo4j full verse data
        driver = await get_driver()
        enriched = []
        async with driver.session() as session:
            for r in results:
                res = await session.run(
                    "MATCH (v:Verse {ref: $ref}) RETURN v {.*} AS verse",
                    ref=r["ref"],
                )
                record = await res.single()
                if record:
                    enriched.append({
                        "verse": record["verse"],
                        "score": r["score"],
                        "semantic_score": r["score"],
                    })

        return {
            "query": q,
            "results": enriched,
            "count": len(enriched),
            "type": "semantic",
            "model": store.embedding_service.model,
        }

    except Exception as e:
        logger.error("semantic_search_failed", query=q, error=str(e))
        raise HTTPException(status_code=503, detail=f"Semantic search unavailable: {e}")


# ── Hybrid Search (RRF) ────────────────────────────────

@router.get("/hybrid")
async def hybrid_search(
    q: str = Query(..., min_length=1, max_length=200),
    book: str | None = None,
    limit: int = Query(default=20, le=100),
    semantic_weight: float = Query(default=0.5, ge=0, le=1),
):
    """Combine fulltext + semantic with Reciprocal Rank Fusion (RRF).

    semantic_weight: 0 = fulltext only, 1 = semantic only, 0.5 = balanced
    """
    k = 60  # RRF constant
    driver = await get_driver()

    # 1. Fulltext results
    ft_results = []
    async with driver.session() as session:
        cypher = """
        CALL db.index.fulltext.queryNodes('verseHebrewText', $query) YIELD node, score
        """
        if book:
            cypher += " WHERE node.book = $book"
        cypher += " RETURN node.ref AS ref, score LIMIT $limit"
        result = await session.run(cypher, query=q, book=book, limit=limit)
        ft_results = [record.data() async for record in result]

    # 2. Semantic results
    sem_results = []
    try:
        store = get_vector_store()
        filters = None
        if book:
            from qdrant_client.models import FieldCondition, MatchValue
            filters = {
                "must": [FieldCondition(key="book", match=MatchValue(value=book))]
            }
        vector_results = await store.search(q, limit=limit, filters=filters)
        sem_results = [{"ref": r["ref"], "score": r["score"]} for r in vector_results]
    except Exception as e:
        logger.warning("hybrid_semantic_failed", error=str(e))

    # 3. RRF scoring
    scores: dict[str, dict] = {}  # ref -> {fulltext_rank, semantic_rank, rrf_score}

    # Weighted RRF: adjust ranks by semantic_weight
    for rank, r in enumerate(ft_results, start=1):
        ref = r["ref"]
        if ref not in scores:
            scores[ref] = {"fulltext_rank": rank, "semantic_rank": None, "score": 0}
        # Fulltext contribution: (1 - weight)
        scores[ref]["score"] += (1 - semantic_weight) / (k + rank)

    for rank, r in enumerate(sem_results, start=1):
        ref = r["ref"]
        if ref not in scores:
            scores[ref] = {"fulltext_rank": None, "semantic_rank": rank, "score": 0}
        else:
            scores[ref]["semantic_rank"] = rank
        # Semantic contribution: weight
        scores[ref]["score"] += semantic_weight / (k + rank)

    # 4. Fetch top results from Neo4j
    top_refs = sorted(scores, key=lambda r: scores[r]["score"], reverse=True)[:limit]
    enriched = []
    if top_refs:
        async with driver.session() as session:
            result = await session.run(
                "MATCH (v:Verse) WHERE v.ref IN $refs RETURN v {.*} AS verse, v.ref AS ref",
                refs=top_refs,
            )
            records = {r["ref"]: r["verse"] async for r in result}

        for ref in top_refs:
            if ref in records:
                s = scores[ref]
                enriched.append({
                    "verse": records[ref],
                    "rrf_score": s["score"],
                    "fulltext_rank": s["fulltext_rank"],
                    "semantic_rank": s["semantic_rank"],
                })

    return {
        "query": q,
        "results": enriched,
        "count": len(enriched),
        "type": "hybrid",
        "semantic_weight": semantic_weight,
        "fulltext_count": len(ft_results),
        "semantic_count": len(sem_results),
    }


# ── Embedding Status ────────────────────────────────────

@router.get("/embeddings/stats")
async def embeddings_stats():
    """Get embedding index statistics."""
    store = get_vector_store()
    return store.get_stats()


@router.post("/embeddings/reindex")
async def reindex_embeddings(
    book: str | None = None,
    batch_size: int = Query(default=32, le=100),
):
    """Trigger background re-indexing of embeddings."""
    from app.celery_app import celery_app

    task = celery_app.send_task(
        "app.tasks.index_embeddings",
        kwargs={"book": book, "batch_size": batch_size},
    )
    return {"task_id": task.id, "status": "queued"}


# ── Unified Search (auto-detect) ─────────────────────────

class SearchResponse(BaseModel):
    query: str
    results: list[dict]
    count: int
    search_type: str
    model: Optional[str] = None
    semantic_weight: Optional[float] = None


@router.get("/", response_model=SearchResponse)
async def unified_search(
    q: str = Query(..., min_length=1, max_length=200),
    book: str | None = None,
    limit: int = Query(default=20, le=100),
    search_type: str = Query(default="hybrid", regex="^(fulltext|semantic|hybrid)$"),
    semantic_weight: float = Query(default=0.5, ge=0, le=1),
):
    """Unified search endpoint — delegates to fulltext/semantic/hybrid."""
    if search_type == "fulltext":
        result = await fulltext_search(q=q, book=book, limit=limit)
    elif search_type == "semantic":
        result = await semantic_search(q=q, book=book, limit=limit)
    else:
        result = await hybrid_search(q=q, book=book, limit=limit, semantic_weight=semantic_weight)

    return SearchResponse(**result)
