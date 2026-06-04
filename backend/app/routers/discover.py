"""AI Discovery API for Torah Knowledge Graph.

Endpoints:
  POST /api/v1/discover/relationships   — AI-powered relationship discovery
  POST /api/v1/discover/entities        — Entity extraction from text
  POST /api/v1/discover/cross_refs      — Find cross-references
  GET  /api/v1/discover/providers       — List available LLM providers
"""

from typing import Any

import structlog
from fastapi import APIRouter, HTTPException

from app.ai_client import LLMClient
from app.neo4j_client import get_driver

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/discover", tags=["discovery"])


@router.get("/providers")
async def list_providers():
    """List available AI providers and their status."""
    return {
        "providers": [
            {"name": "ollama", "label": "Ollama (Local)", "requires_key": False},
            {"name": "claude", "label": "Anthropic Claude", "requires_key": True},
            {"name": "openrouter", "label": "OpenRouter (Multi-model)", "requires_key": True},
            {"name": "openai", "label": "OpenAI", "requires_key": True},
        ],
        "default": "ollama",
    }


@router.post("/relationships")
async def discover_relationships(payload: dict[str, Any]) -> dict[str, Any]:
    """Discover relationships in a Torah text using AI.

    Request body:
      {
        "verse_ref": "Genesis 1:1",
        "provider": "claude",  // optional: ollama | claude | openrouter | openai
        "context_window": 3     // optional: verses before/after
      }
    """
    verse_ref = payload.get("verse_ref", "")
    provider = payload.get("provider", "ollama")
    context_window = payload.get("context_window", 3)

    if not verse_ref:
        raise HTTPException(status_code=400, detail="verse_ref is required")

    # Step 1: Fetch the verse + context from Neo4j
    driver = await get_driver()
    async with driver.session() as session:
        # Get target verse
        result = await session.run(
            "MATCH (v:Verse {ref: $ref}) RETURN v.text_hebrew AS text, v.text_hebrew_normalized AS norm",
            ref=verse_ref,
        )
        record = await result.single()
        if not record:
            raise HTTPException(status_code=404, detail=f"Verse {verse_ref} not found")

        target_text = record["text"] or ""
        target_norm = record["norm"] or ""

        # Get context verses
        result = await session.run(
            """
            MATCH (v:Verse {ref: $ref})
            WITH v.book AS book, v.chapter AS chapter, v.verse_number AS vn
            MATCH (ctx:Verse)
            WHERE ctx.book = book AND ctx.chapter = chapter
              AND ctx.verse_number >= $start AND ctx.verse_number <= $end
            RETURN ctx.ref AS ref, ctx.text_hebrew AS text
            ORDER BY ctx.verse_number
            """,
            ref=verse_ref, start=max(1, payload.get("start_verse", 1)), end=payload.get("end_verse", 5),
        )
        context = [{"ref": r["ref"], "text": r["text"]} async for r in result]

    # Step 2: Call LLM for discovery
    client = LLMClient(provider=provider)
    full_text = "\n\n".join([f"{v['ref']}: {v['text']}" for v in context])

    try:
        discovery = await client.discover_relationships(
            source_text=full_text,
            source_ref=verse_ref,
        )
    except Exception as e:
        logger.error("discovery_failed", error=str(e), provider=provider, ref=verse_ref)
        raise HTTPException(status_code=503, detail=f"AI discovery failed: {e}")

    return {
        "source_ref": verse_ref,
        "provider": discovery["metadata"]["provider"],
        "model": discovery["metadata"]["model"],
        "context_verses": len(context),
        "discovery": discovery["discovery"],
        "usage": discovery["metadata"].get("usage", {}),
    }


@router.post("/entities")
async def extract_entities(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract entities from arbitrary Hebrew/English Torah text.

    Request body:
      {
        "text": "וַיֹּאמֶר ה' אֶל־מֹשֶׁה...",
        "provider": "claude"
      }
    """
    text = payload.get("text", "")
    provider = payload.get("provider", "ollama")

    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    client = LLMClient(provider=provider)
    system = """You are a Torah entity extractor. Identify all named entities in the provided text.
Return ONLY a JSON array of entities."""

    prompt = f"""Extract all named entities from this Torah text:

{text[:3000]}

Return JSON:
{{
  "entities": [
    {{"name": "English name", "nameHe": "Hebrew name", "type": "Person|Place|Concept|Mitzvah|Event|Text|Object", "role": "optional description"}}
  ]
}}"""

    try:
        result = await client.complete(prompt, system=system, json_mode=True)
        parsed = __import__("json").loads(result["text"])
        return {
            "entities": parsed.get("entities", []),
            "provider": result["provider"],
            "model": result["model"],
            "usage": result.get("usage", {}),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Entity extraction failed: {e}")


@router.post("/cross_refs")
async def find_cross_references(payload: dict[str, Any]) -> dict[str, Any]:
    """Find cross-references to a verse using full-text + AI.

    Request body:
      {
        "verse_ref": "Genesis 1:1",
        "limit": 10
      }
    """
    verse_ref = payload.get("verse_ref", "")
    limit = payload.get("limit", 10)

    if not verse_ref:
        raise HTTPException(status_code=400, detail="verse_ref is required")

    driver = await get_driver()
    async with driver.session() as session:
        # Get the verse normalized text
        result = await session.run(
            "MATCH (v:Verse {ref: $ref}) RETURN v.text_hebrew_normalized AS norm",
            ref=verse_ref,
        )
        record = await result.single()
        if not record or not record["norm"]:
            raise HTTPException(status_code=404, detail=f"Verse {verse_ref} not found or not normalized")

        text_norm = record["norm"]
        # Extract key Hebrew words
        words = [w for w in text_norm.split() if len(w) >= 3][:5]
        query = " OR ".join(words)

        # Full-text search
        result = await session.run(
            """
            CALL db.index.fulltext.queryNodes('verseHebrewNormalized', $q) YIELD node, score
            WHERE node.ref <> $ref
            RETURN node.ref AS ref, node.text_hebrew AS text_he, score
            ORDER BY score DESC LIMIT $limit
            """,
            q=query, ref=verse_ref, limit=limit,
        )
        matches = [{"ref": r["ref"], "text_preview": r["text_he"][:150], "score": round(r["score"], 3)} async for r in result]

    return {
        "source_ref": verse_ref,
        "search_words": words,
        "matches": matches,
        "count": len(matches),
    }
