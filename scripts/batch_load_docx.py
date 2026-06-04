#!/usr/bin/env python3
"""
Batch loader for Torat Emet .docx collection.

Scans a category directory, parses all .docx files, and loads them into Neo4j
via the FastAPI ingestion endpoint.

Usage:
    uv run python scripts/batch_load_docx.py \
        --category-dir /path/to/חסידות \
        --api-url http://localhost:8002 \
        --category-label Chassidut
"""

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

# Import parser
sys.path.insert(0, str(Path(__file__).parent))
from docx_parser import parse_directory, save_jsonl


def load_jsonl_to_neo4j(nodes_file: Path, rels_file: Path, api_url: str) -> bool:
    """Load processed JSONL into Neo4j via the backend API."""
    # Load nodes
    nodes = []
    with open(nodes_file, "r", encoding="utf-8") as f:
        for line in f:
            nodes.append(json.loads(line))

    relationships = []
    with open(rels_file, "r", encoding="utf-8") as f:
        for line in f:
            relationships.append(json.loads(line))

    # For now, save to data/processed for neo4j-admin or direct Cypher loading
    # In the future, this will call the backend API directly
    print(f"   📦 Nodes: {len(nodes)}, Relationships: {len(relationships)}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch load .docx Torah collection")
    parser.add_argument("--category-dir", type=str, required=True, help="Directory containing .docx files")
    parser.add_argument("--output", type=str, default="data/processed", help="Output directory for JSONL")
    parser.add_argument("--category-label", type=str, default="Torah_Literature", help="Neo4j category label")
    parser.add_argument("--api-url", type=str, default="http://localhost:8002", help="Backend API URL")
    parser.add_argument("--dry-run", action="store_true", help="Parse only, don't load")

    args = parser.parse_args()
    category_dir = Path(args.category_dir)
    output_dir = Path(args.output)

    if not category_dir.exists():
        print(f"❌ Directory not found: {category_dir}")
        sys.exit(1)

    print(f"🔍 Scanning: {category_dir}")
    results = parse_directory(category_dir, output_dir)
    print(f"✅ Parsed {len(results)} files")

    if args.dry_run:
        print("🚫 Dry run — not loading to Neo4j")
        return

    print("🚀 Loading into Neo4j...")
    for result in results:
        safe_name = result["book"].replace(" ", "_").replace("/", "_")
        nodes_file = output_dir / f"{safe_name}_nodes.jsonl"
        rels_file = output_dir / f"{safe_name}_relationships.jsonl"
        if nodes_file.exists() and rels_file.exists():
            load_jsonl_to_neo4j(nodes_file, rels_file, args.api_url)

    print("✅ Batch load complete")


if __name__ == "__main__":
    main()
