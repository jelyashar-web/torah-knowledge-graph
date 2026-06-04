#!/usr/bin/env python3
"""
Update all existing Verse nodes in Neo4j with text_hebrew_normalized.

Runs in batches and sets the new property for every Verse that has
 text_hebrew but not yet text_hebrew_normalized.

Usage:
    uv run python scripts/update_hebrew_normalized.py
"""

import argparse
import asyncio

from neo4j import AsyncGraphDatabase

from hebrew_utils import normalize_hebrew


NEO4J_URI = "bolt://localhost:7688"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "torah-graph-secure"


async def update_verses(driver, batch_size: int = 500):
    """Fetch verses in batches, normalize, and update."""
    updated = 0
    skipped = 0
    page = 0

    while True:
        async with driver.session() as session:
            result = await session.run(
                """
                MATCH (v:Verse)
                WHERE v.text_hebrew IS NOT NULL
                  AND (v.text_hebrew_normalized IS NULL OR v.text_hebrew_normalized = '')
                RETURN v.id AS id, v.text_hebrew AS text_hebrew
                LIMIT $batch_size
                """,
                batch_size=batch_size,
            )
            records = await result.data()

        if not records:
            break

        batch = []
        for rec in records:
            raw = rec["text_hebrew"]
            normalized = normalize_hebrew(raw)
            batch.append({"id": rec["id"], "normalized": normalized})

        async with driver.session() as session:
            await session.run(
                """
                UNWIND $batch AS item
                MATCH (v:Verse {id: item.id})
                SET v.text_hebrew_normalized = item.normalized
                """,
                batch=batch,
            )

        updated += len(batch)
        page += 1
        print(f"   Batch {page}: updated {len(batch)} verses")

    print(f"\n✅ Total verses updated: {updated}")
    print(f"⏭️  Skipped (already normalized): {skipped}")


async def main():
    parser = argparse.ArgumentParser(description="Add Hebrew normalized text to Neo4j Verse nodes")
    parser.add_argument("--neo4j-uri", type=str, default=NEO4J_URI)
    parser.add_argument("--neo4j-user", type=str, default=NEO4J_USER)
    parser.add_argument("--neo4j-password", type=str, default=NEO4J_PASSWORD)
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size for updates")
    parser.add_argument("--dry-run", action="store_true", help="Count only, do not update")

    args = parser.parse_args()

    driver = AsyncGraphDatabase.driver(
        args.neo4j_uri,
        auth=(args.neo4j_user, args.neo4j_password),
    )

    if args.dry_run:
        async with driver.session() as session:
            result = await session.run(
                """
                MATCH (v:Verse)
                WHERE v.text_hebrew IS NOT NULL
                  AND (v.text_hebrew_normalized IS NULL OR v.text_hebrew_normalized = '')
                RETURN count(v) AS cnt
                """
            )
            record = await result.single()
            print(f"📊 Dry run: {record['cnt']} verses need normalization")
        await driver.close()
        return

    print("🚀 Updating Hebrew normalization for all Verse nodes...")
    await update_verses(driver, args.batch_size)
    await driver.close()
    print("✅ Done")


if __name__ == "__main__":
    asyncio.run(main())
