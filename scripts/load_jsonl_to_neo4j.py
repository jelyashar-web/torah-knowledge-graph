#!/usr/bin/env python3
"""
Load processed JSONL files into Neo4j via async Cypher.

Usage:
    python scripts/load_jsonl_to_neo4j.py --nodes data/processed/chassidut/*.jsonl --batch-size 500
"""

import argparse
import asyncio
import json
from pathlib import Path

from neo4j import AsyncGraphDatabase


NEO4J_URI = "bolt://localhost:7688"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "torah-graph-secure"


async def load_nodes(driver, nodes_file: Path, batch_size: int = 500):
    nodes = []
    with open(nodes_file, "r", encoding="utf-8") as f:
        for line in f:
            nodes.append(json.loads(line))

    for i in range(0, len(nodes), batch_size):
        batch = nodes[i : i + batch_size]
        async with driver.session() as session:
            await session.run(
                """
                UNWIND $batch AS node
                CALL apoc.merge.node(
                    [node.label],
                    {id: node.id},
                    node.properties
                ) YIELD node as n
                RETURN count(n)
                """,
                batch=batch,
            )
        print(f"   Nodes batch {i // batch_size + 1}: {len(batch)} loaded")

    print(f"✅ Nodes loaded: {len(nodes)} from {nodes_file.name}")


async def load_relationships(driver, rels_file: Path, batch_size: int = 500):
    rels = []
    with open(rels_file, "r", encoding="utf-8") as f:
        for line in f:
            rels.append(json.loads(line))

    for i in range(0, len(rels), batch_size):
        batch = rels[i : i + batch_size]
        async with driver.session() as session:
            await session.run(
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
                RETURN count(r)
                """,
                batch=batch,
            )
        print(f"   Rels batch {i // batch_size + 1}: {len(batch)} loaded")

    print(f"✅ Relationships loaded: {len(rels)} from {rels_file.name}")


async def main():
    parser = argparse.ArgumentParser(description="Load JSONL into Neo4j")
    parser.add_argument("--nodes", type=str, required=True, help="Path to nodes JSONL file")
    parser.add_argument("--relationships", type=str, required=True, help="Path to relationships JSONL file")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size for UNWIND")
    parser.add_argument("--neo4j-uri", type=str, default=NEO4J_URI)
    parser.add_argument("--neo4j-user", type=str, default=NEO4J_USER)
    parser.add_argument("--neo4j-password", type=str, default=NEO4J_PASSWORD)

    args = parser.parse_args()
    nodes_file = Path(args.nodes)
    rels_file = Path(args.relationships)

    driver = AsyncGraphDatabase.driver(
        args.neo4j_uri,
        auth=(args.neo4j_user, args.neo4j_password),
    )

    print(f"🚀 Loading {nodes_file.stem} into Neo4j...")
    await load_nodes(driver, nodes_file, args.batch_size)
    await load_relationships(driver, rels_file, args.batch_size)

    await driver.close()
    print("✅ Done")


if __name__ == "__main__":
    asyncio.run(main())
