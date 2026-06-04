#!/usr/bin/env python3
"""
Load processed JSONL nodes and relationships into Neo4j.

Usage:
    uv run --with neo4j python scripts/load_to_neo4j.py --nodes-dir data/processed/ --relationships-dir data/processed/
"""

import argparse
import json
from pathlib import Path

from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "torah-graph-secure"
BATCH_SIZE = 500


def load_nodes(driver: GraphDatabase, nodes_dir: Path) -> dict[str, int]:
    """Load all *_nodes.jsonl files into Neo4j."""
    files = sorted(nodes_dir.glob("*_nodes.jsonl"))
    total = 0
    for f in files:
        print(f"📥 Loading nodes from {f.name}...")
        nodes: list[dict] = []
        with open(f, "r", encoding="utf-8") as fh:
            for line in fh:
                nodes.append(json.loads(line))

        with driver.session() as session:
            for i in range(0, len(nodes), BATCH_SIZE):
                batch = nodes[i : i + BATCH_SIZE]
                result = session.run(
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
                total += result.single()["cnt"]
        print(f"   ✅ {len(nodes)} nodes loaded")
    return {"total_nodes": total}


def load_relationships(driver: GraphDatabase, rels_dir: Path) -> dict[str, int]:
    """Load all *_relationships.jsonl files into Neo4j."""
    files = sorted(rels_dir.glob("*_relationships.jsonl"))
    total = 0
    for f in files:
        print(f"📥 Loading relationships from {f.name}...")
        rels: list[dict] = []
        with open(f, "r", encoding="utf-8") as fh:
            for line in fh:
                rels.append(json.loads(line))

        with driver.session() as session:
            for i in range(0, len(rels), BATCH_SIZE):
                batch = rels[i : i + BATCH_SIZE]
                result = session.run(
                    """
                    UNWIND $batch AS rel
                    MATCH (a {id: rel.from_id})
                    MATCH (b {id: rel.to_id})
                    CALL apoc.merge.relationship(a, rel.type, {}, rel.properties, b) YIELD rel as r
                    RETURN count(r) as cnt
                    """,
                    batch=batch,
                )
                total += result.single()["cnt"]
        print(f"   ✅ {len(rels)} relationships loaded")
    return {"total_rels": total}


def main() -> None:
    parser = argparse.ArgumentParser(description="Load JSONL into Neo4j")
    parser.add_argument("--nodes-dir", type=str, default="data/processed")
    parser.add_argument("--relationships-dir", type=str, default="data/processed")
    args = parser.parse_args()

    nodes_dir = Path(args.nodes_dir)
    rels_dir = Path(args.relationships_dir)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    print("🔗 Connected to Neo4j")

    # Clear existing data (optional, but safe for visualization)
    with driver.session() as session:
        print("🧹 Clearing existing graph data...")
        session.run("MATCH (n) DETACH DELETE n")
        print("   ✅ Graph cleared")

    node_result = load_nodes(driver, nodes_dir)
    rel_result = load_relationships(driver, rels_dir)

    print(f"\n🎉 Load complete!")
    print(f"   Nodes: {node_result['total_nodes']}")
    print(f"   Relationships: {rel_result['total_rels']}")

    driver.close()


if __name__ == "__main__":
    main()
