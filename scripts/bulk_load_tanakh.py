#!/usr/bin/env python3
"""
Bulk load all Tanakh JSONL files into Neo4j.

Loads nodes first (Book → Chapter → Verse), then relationships (PART_OF).
Uses APOC merge to prevent duplicates when re-running.

Usage:
    uv run python scripts/bulk_load_tanakh.py --data-dir data/processed/ --batch-size 500
"""

import argparse
import asyncio
import json
from pathlib import Path

from neo4j import AsyncGraphDatabase


NEO4J_URI = "bolt://localhost:7688"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "torah-graph-secure"


async def load_nodes_file(driver, nodes_file: Path, batch_size: int = 500) -> int:
    """Load a single nodes JSONL file."""
    nodes = []
    with open(nodes_file, "r", encoding="utf-8") as f:
        for line in f:
            nodes.append(json.loads(line))

    total = 0
    for i in range(0, len(nodes), batch_size):
        batch = nodes[i : i + batch_size]
        async with driver.session() as session:
            result = await session.run(
                """
                UNWIND $batch AS node
                CALL apoc.merge.node(
                    [node.label],
                    {id: node.id},
                    node.properties
                ) YIELD node as n
                RETURN count(n) as cnt
                """,
                batch=batch,
            )
            record = await result.single()
            total += record["cnt"] if record else len(batch)
        print(f"   [{nodes_file.stem}] Nodes batch {i // batch_size + 1}: {len(batch)} loaded")

    print(f"✅ Nodes loaded: {total} from {nodes_file.name}")
    return total


async def load_rels_file(driver, rels_file: Path, batch_size: int = 500) -> int:
    """Load a single relationships JSONL file."""
    rels = []
    with open(rels_file, "r", encoding="utf-8") as f:
        for line in f:
            rels.append(json.loads(line))

    total = 0
    for i in range(0, len(rels), batch_size):
        batch = rels[i : i + batch_size]
        async with driver.session() as session:
            result = await session.run(
                """
                UNWIND $batch AS rel
                MATCH (a {id: rel.from_id})
                MATCH (b {id: rel.to_id})
                CALL apoc.merge.relationship(
                    a,
                    rel.type,
                    {},
                    rel.properties,
                    b
                ) YIELD rel as r
                RETURN count(r) as cnt
                """,
                batch=batch,
            )
            record = await result.single()
            total += record["cnt"] if record else len(batch)
        print(f"   [{rels_file.stem}] Rels batch {i // batch_size + 1}: {len(batch)} loaded")

    print(f"✅ Relationships loaded: {total} from {rels_file.name}")
    return total


async def main():
    parser = argparse.ArgumentParser(description="Bulk load Tanakh JSONL into Neo4j")
    parser.add_argument("--data-dir", type=str, default="data/processed", help="Directory containing *_nodes.jsonl and *_relationships.jsonl files")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size for UNWIND")
    parser.add_argument("--neo4j-uri", type=str, default=NEO4J_URI)
    parser.add_argument("--neo4j-user", type=str, default=NEO4J_USER)
    parser.add_argument("--neo4j-password", type=str, default=NEO4J_PASSWORD)
    parser.add_argument("--dry-run", action="store_true", help="Count files only, do not load")

    args = parser.parse_args()
    data_dir = Path(args.data_dir)

    nodes_files = sorted(data_dir.glob("*_nodes.jsonl"))
    rels_files = sorted(data_dir.glob("*_relationships.jsonl"))

    # Exclude bulk_import and chassidut/test subdirs from Tanakh load
    nodes_files = [f for f in nodes_files if f.parent == data_dir]
    rels_files = [f for f in rels_files if f.parent == data_dir]

    print(f"📚 Found {len(nodes_files)} nodes files and {len(rels_files)} relationships files")

    if args.dry_run:
        total_nodes = sum(1 for f in nodes_files for _ in open(f, "r", encoding="utf-8"))
        total_rels = sum(1 for f in rels_files for _ in open(f, "r", encoding="utf-8"))
        print(f"   Total nodes to load: {total_nodes}")
        print(f"   Total relationships to load: {total_rels}")
        return

    driver = AsyncGraphDatabase.driver(
        args.neo4j_uri,
        auth=(args.neo4j_user, args.neo4j_password),
    )

    # --- Phase 1: Load all nodes ---
    print(f"\n{'='*60}")
    print("📦 PHASE 1: Loading all nodes...")
    print(f"{'='*60}")
    total_nodes = 0
    for nodes_file in nodes_files:
        total_nodes += await load_nodes_file(driver, nodes_file, args.batch_size)

    # --- Phase 2: Load all relationships ---
    print(f"\n{'='*60}")
    print("🔗 PHASE 2: Loading all relationships...")
    print(f"{'='*60}")
    total_rels = 0
    for rels_file in rels_files:
        total_rels += await load_rels_file(driver, rels_file, args.batch_size)

    await driver.close()

    print(f"\n{'='*60}")
    print("🎉 BULK LOAD COMPLETE")
    print(f"{'='*60}")
    print(f"   Total nodes loaded:     {total_nodes}")
    print(f"   Total relationships:    {total_rels}")
    print(f"   Files processed:        {len(nodes_files)} nodes + {len(rels_files)} rels")


if __name__ == "__main__":
    asyncio.run(main())
