#!/usr/bin/env python3
"""Batch generate embeddings for all verses and index into Qdrant.

Usage:
    uv run python scripts/generate_embeddings.py --provider ollama --model nomic-embed-text
    uv run python scripts/generate_embeddings.py --provider sentence_transformers --model BAAI/bge-m3
    uv run python scripts/generate_embeddings.py --all-books --batch-size 32

Progress is shown via tqdm. Existing embeddings are skipped.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.embeddings import TorahEmbeddingService, TorahVectorStore
from app.neo4j_client import neo4j_client


async def get_all_verses(book_filter: str = None) -> list[dict]:
    """Fetch all verses from Neo4j."""
    print("Fetching verses from Neo4j...")

    if book_filter:
        cypher = """
        MATCH (v:Verse {book: $book})
        RETURN v.ref as ref, v.hebrew as hebrew, v.english as english,
               v.book as book, v.chapter as chapter, v.verse as verse
        """
        records, _, _ = neo4j_client.driver.execute_query(cypher, book=book_filter)
    else:
        cypher = """
        MATCH (v:Verse)
        RETURN v.ref as ref, v.hebrew as hebrew, v.english as english,
               v.book as book, v.chapter as chapter, v.verse as verse
        """
        records, _, _ = neo4j_client.driver.execute_query(cypher)

    verses = []
    for r in records:
        verses.append({
            "ref": r["ref"],
            "hebrew": r.get("hebrew"),
            "english": r.get("english"),
            "book": r.get("book"),
            "chapter": r.get("chapter"),
            "verse": r.get("verse"),
        })

    print(f"Found {len(verses)} verses")
    return verses


async def main():
    parser = argparse.ArgumentParser(description="Generate Torah embeddings")
    parser.add_argument("--provider", default="ollama", choices=["ollama", "sentence_transformers", "openai", "kimi"])
    parser.add_argument("--model", default=None, help="Model name (defaults to provider default)")
    parser.add_argument("--book", default=None, help="Filter to specific book")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for embedding")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of verses")
    parser.add_argument("--skip-existing", action="store_true", help="Skip verses already in Qdrant")
    parser.add_argument("--stats-only", action="store_true", help="Only show Qdrant stats")

    args = parser.parse_args()

    # Initialize services
    embedding_service = TorahEmbeddingService(
        provider=args.provider,
        model=args.model,
    )
    vector_store = TorahVectorStore()

    # Stats only
    if args.stats_only:
        stats = vector_store.get_stats()
        print(json.dumps(stats, indent=2, default=str))
        return

    # Fetch verses
    verses = await get_all_verses(args.book)
    if args.limit:
        verses = verses[:args.limit]

    if not verses:
        print("No verses found")
        return

    print(f"\nEmbedding {len(verses)} verses using {args.provider}/{embedding_service.model}")
    print(f"Dimension: {embedding_service._dimension}")
    print("=" * 60)

    start_time = datetime.now()

    # Progress callback
    def on_progress(current: int, total: int):
        pct = (current / total) * 100
        bar = "█" * int(pct // 2) + "░" * (50 - int(pct // 2))
        print(f"\r[{bar}] {current}/{total} ({pct:.1f}%)", end="", flush=True)

    # Batch index
    await vector_store.index_verses_batch(verses, progress_callback=on_progress)

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n\nDone! {len(verses)} verses indexed in {elapsed:.1f}s")
    print(f"Rate: {len(verses)/elapsed:.1f} verses/sec")

    # Final stats
    stats = vector_store.get_stats()
    print(f"\nQdrant collection: {stats.get('vectors_count')} vectors")
    print(f"Model: {stats.get('model')}")


if __name__ == "__main__":
    asyncio.run(main())
