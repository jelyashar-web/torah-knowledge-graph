#!/usr/bin/env python3
"""
Synchronous bulk import of Torat Emet .docx collection into Neo4j.

Optimized for speed: single Neo4j session, no disk I/O, batch size 1000.

Usage:
    python scripts/bulk_import_sync.py \
        --source-dir /path/to/collection \
        --limit 50
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).parent))
from docx_parser import extract_docx_text, parse_chumash, parse_free_form

NEO4J_URI = "bolt://localhost:7688"
NEO4J_AUTH = ("neo4j", "torah-graph-secure")

SKIP_PATTERNS = [
    re.compile(r"מקרא ותרגום"),
    re.compile(r"מקראות גדולות"),
    re.compile(r"- אבן עזרא"),
    re.compile(r"- בעל הטורים"),
    re.compile(r"- דעת זקנים"),
    re.compile(r"- כלי יקר"),
    re.compile(r"- ספורנו"),
    re.compile(r"- רמבן"),
    re.compile(r"- רשי"),
    re.compile(r"- שפתי חכמים"),
    re.compile(r"- אור החיים"),
    re.compile(r"תרגום אונקלוס"),
    re.compile(r"תרגום יונתן"),
    re.compile(r"- מפורש"),
]


def should_skip(file_path: Path) -> bool:
    name = file_path.name
    for pattern in SKIP_PATTERNS:
        if pattern.search(name):
            return True
    return False


def load_batch(driver, nodes: list, rels: list, batch_size: int = 1000):
    """Load nodes and relationships in batches using a single session."""
    with driver.session() as session:
        # Load nodes
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i : i + batch_size]
            session.run(
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

        # Load relationships
        for i in range(0, len(rels), batch_size):
            batch = rels[i : i + batch_size]
            session.run(
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=str, required=True)
    parser.add_argument("--neo4j-uri", type=str, default=NEO4J_URI)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    docx_files = list(source_dir.rglob("*.docx"))

    # Filter out commentaries/index files
    files_to_process = [f for f in docx_files if not should_skip(f)]
    skipped_count = len(docx_files) - len(files_to_process)

    if args.limit:
        files_to_process = files_to_process[:args.limit]

    print(f"📊 Total files: {len(docx_files)}")
    print(f"⏭️  Skipped (commentaries/translations): {skipped_count}")
    print(f"🚀 Will process: {len(files_to_process)}")
    print(f"{'='*60}\n")

    driver = GraphDatabase.driver(args.neo4j_uri, auth=NEO4J_AUTH)

    total_nodes = 0
    total_rels = 0
    loaded_count = 0
    error_count = 0
    start_time = time.time()

    for i, file_path in enumerate(files_to_process, 1):
        file_start = time.time()
        try:
            paragraphs = extract_docx_text(file_path)
            if not paragraphs:
                continue

            book_title = file_path.stem
            structured = parse_chumash(paragraphs, book_title)
            if len(structured["nodes"]) <= 1:
                structured = parse_free_form(paragraphs, book_title)

            nodes = structured["nodes"]
            rels = structured["relationships"]

            if len(nodes) <= 1:
                continue

            load_batch(driver, nodes, rels, args.batch_size)

            loaded_count += 1
            total_nodes += len(nodes)
            total_rels += len(rels)
            elapsed = time.time() - start_time
            avg_per_file = elapsed / loaded_count if loaded_count > 0 else 0
            eta = avg_per_file * (len(files_to_process) - i)

            print(
                f"[{i}/{len(files_to_process)}] ✅ {file_path.name[:50]:<50} "
                f"| Nodes: {len(nodes):>5} | Rels: {len(rels):>5} "
                f"| ETA: {eta/60:.0f}m"
            )

        except Exception as e:
            error_count += 1
            print(f"[{i}/{len(files_to_process)}] ❌ {file_path.name[:50]} | Error: {e}")

    driver.close()

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"📊 BULK IMPORT COMPLETE")
    print(f"{'='*60}")
    print(f"   ✅ Files loaded:     {loaded_count}")
    print(f"   ❌ Errors:           {error_count}")
    print(f"   📦 Total nodes:       {total_nodes:,}")
    print(f"   🔗 Total rels:        {total_rels:,}")
    print(f"   ⏱️  Time:              {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"   ⚡ Avg per file:      {elapsed/loaded_count:.1f}s" if loaded_count > 0 else "")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
