"""Search API: fulltext, semantic, hybrid."""

from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import settings
from app.neo4j_client import get_driver

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("/fulltext")
async def fulltext_search(
    q: str = Query(..., min_length=1, max_length=200),
    book: str | None = None,
    limit: int = 20,
):
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

    return {"query": q, "results": records, "count": len(records)}


@router.get("/semantic")
async def semantic_search(
    q: str = Query(..., min_length=1, max_length=200),
    book: str | None = None,
    limit: int = 20,
):
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503, detail="Semantic search unavailable: no OPENAI_API_KEY configured"
        )

    import openai
    from qdrant_client import QdrantClient

    client = openai.OpenAI(api_key=settings.openai_api_key)
    qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

    # Embed query
    emb = client.embeddings.create(input=[q], model=settings.embedding_model)
    vector = emb.data[0].embedding

    # Search Qdrant
    filter_kwargs = {}
    if book:
        filter_kwargs["query_filter"] = {
            "must": [{"key": "book", "match": {"value": book}}]
        }

    search_result = qdrant.search(
        collection_name="torah_verses",
        query_vector=vector,
        limit=limit,
        **filter_kwargs,
    )

    # Enrich with Neo4j
    driver = await get_driver()
    enriched = []
    async with driver.session() as session:
        for point in search_result:
            result = await session.run(
                "MATCH (v:Verse {id: $id}) RETURN v {.*} AS verse",
                id=point.id,
            )
            record = await result.single()
            if record:
                enriched.append(
                    {
                        "verse": record["verse"],
                        "score": point.score,
                    }
                )

    return {"query": q, "results": enriched, "count": len(enriched)}


@router.get("/hybrid")
async def hybrid_search(
    q: str = Query(..., min_length=1, max_length=200),
    book: str | None = None,
    limit: int = 20,
):
    """Combine fulltext + semantic with Reciprocal Rank Fusion (RRF)."""
    k = 60  # RRF constant

    # Fulltext results
    driver = await get_driver()
    ft_results = []
    async with driver.session() as session:
        cypher = """
        CALL db.index.fulltext.queryNodes('verseHebrewText', $query) YIELD node, score
        """
        if book:
            cypher += " WHERE node.book = $book"
        cypher += " RETURN node.id AS id, score LIMIT $limit"
        result = await session.run(cypher, query=q, book=book, limit=limit)
        ft_results = [record.data() async for record in result]

    # Semantic results
    sem_results = []
    if settings.openai_api_key:
        import openai
        from qdrant_client import QdrantClient

        client = openai.OpenAI(api_key=settings.openai_api_key)
        qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        emb = client.embeddings.create(input=[q], model=settings.embedding_model)
        vector = emb.data[0].embedding

        filter_kwargs = {}
        if book:
            filter_kwargs["query_filter"] = {
                "must": [{"key": "book", "match": {"value": book}}]
            }

        qr = qdrant.search(
            collection_name="torah_verses",
            query_vector=vector,
            limit=limit,
            **filter_kwargs,
        )
        sem_results = [{"id": p.id, "score": p.score} for p in qr]

    # RRF scoring
    scores: dict[str, float] = {}
    for rank, r in enumerate(ft_results, start=1):
        scores[r["id"]] = scores.get(r["id"], 0) + 1 / (k + rank)
    for rank, r in enumerate(sem_results, start=1):
        scores[r["id"]] = scores.get(r["id"], 0) + 1 / (k + rank)

    # Fetch top results from Neo4j
    top_ids = sorted(scores, key=scores.get, reverse=True)[:limit]
    enriched = []
    if top_ids:
        async with driver.session() as session:
            result = await session.run(
                "MATCH (v:Verse) WHERE v.id IN $ids RETURN v {.*} AS verse, v.id AS id",
                ids=top_ids,
            )
            records = {r["id"]: r["verse"] async for r in result}

        for vid in top_ids:
            if vid in records:
                enriched.append({"verse": records[vid], "rrf_score": scores[vid]})

    return {"query": q, "results": enriched, "count": len(enriched)}
