#!/usr/bin/env python3
"""
Bulk import the entire Torat Emet collection into Neo4j.

Scans all category directories, parses .docx files, filters out
index-only files (Mikra v'Targum, Mefarshim), and loads real
content into Neo4j.

Usage:
    python scripts/bulk_import_collection.py \
        --source-dir "/home/vix/Documents/ספרי קודש/drive-download-20260604T114723Z-3-001" \
        --neo4j-uri bolt://localhost:7688 \
        --batch-size 500
"""

import argparse
import asyncio
import json
import re
import sys
import time
from pathlib import Path

try:
    import structlog
    logger = structlog.get_logger()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    _logger = logging.getLogger("bulk_import")
    class _Wrap:
        def info(self, msg, **kwargs): _logger.info(msg + " | " + " ".join(f"{k}={v}" for k, v in kwargs.items()))
        def warning(self, msg, **kwargs): _logger.warning(msg + " | " + " ".join(f"{k}={v}" for k, v in kwargs.items()))
        def error(self, msg, **kwargs): _logger.error(msg + " | " + " ".join(f"{k}={v}" for k, v in kwargs.items()))
    logger = _Wrap()

sys.path.insert(0, str(Path(__file__).parent))
from docx_parser import extract_docx_text, parse_chumash, parse_free_form, save_jsonl


# Files/directories to skip
SKIP_PATTERNS = [
    re.compile(r"מקרא ותרגום"),           # Only verse indices
    re.compile(r"מקראות גדולות"),         # Only verse indices
    re.compile(r"- אבן עזרא"),            # Commentary only
    re.compile(r"- בעל הטורים"),          # Commentary only
    re.compile(r"- דעת זקנים"),           # Commentary only
    re.compile(r"- כלי יקר"),             # Commentary only
    re.compile(r"- ספורנו"),              # Commentary only
    re.compile(r"- רמבן"),                 # Commentary only
    re.compile(r"- רשי"),                  # Commentary only
    re.compile(r"- שפתי חכמים"),          # Commentary only
    re.compile(r"- אור החיים"),           # Commentary only
    re.compile(r"תרגום אונקלוס"),          # Translation only
    re.compile(r"תרגום יונתן"),           # Translation only
    re.compile(r"- מפורש"),                 # Commentary only
]


def should_skip(file_path: Path) -> str | None:
    """Return skip reason if file should be skipped, None otherwise."""
    name = file_path.name
    for pattern in SKIP_PATTERNS:
        if pattern.search(name):
            return f"SKIP: matches '{pattern.pattern}'"
    return None


async def load_nodes_direct(driver, nodes: list, batch_size: int = 1000):
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


async def load_rels_direct(driver, rels: list, batch_size: int = 1000):
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


async def import_file(file_path: Path, output_dir: Path, driver, batch_size: int) -> dict:
    """Parse a single .docx and load into Neo4j."""
    result = {"file": str(file_path), "status": "unknown", "nodes": 0, "rels": 0, "error": None}

    skip_reason = should_skip(file_path)
    if skip_reason:
        result["status"] = "skipped"
        result["error"] = skip_reason
        return result

    try:
        paragraphs = extract_docx_text(file_path)
        if not paragraphs:
            result["status"] = "empty"
            return result

        book_title = file_path.stem
        # Try structured parsing first
        structured = parse_chumash(paragraphs, book_title)
        if len(structured["nodes"]) <= 1:
            structured = parse_free_form(paragraphs, book_title)

        nodes = structured["nodes"]
        rels = structured["relationships"]

        # Skip if only Book node (no real content)
        if len(nodes) <= 1:
            result["status"] = "no_content"
            return result

        # Load directly into Neo4j from memory (no disk I/O)
        await load_nodes_direct(driver, nodes, batch_size)
        await load_rels_direct(driver, rels, batch_size)

        result["status"] = "loaded"
        result["nodes"] = len(nodes)
        result["rels"] = len(rels)

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error("import_failed", file=str(file_path), error=str(e))

    return result


async def main():
    parser = argparse.ArgumentParser(description="Bulk import Torat Emet collection")
    parser.add_argument("--source-dir", type=str, required=True, help="Root directory of the collection")
    parser.add_argument("--output", type=str, default="data/processed/bulk_import", help="Output directory")
    parser.add_argument("--neo4j-uri", type=str, default="bolt://localhost:7688")
    parser.add_argument("--neo4j-user", type=str, default="neo4j")
    parser.add_argument("--neo4j-password", type=str, default="torah-graph-secure")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files to process (for testing)")
    parser.add_argument("--dry-run", action="store_true", help="Parse only, do not load to Neo4j")

    args = parser.parse_args()
    source_dir = Path(args.source_dir)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all .docx files
    docx_files = list(source_dir.rglob("*.docx"))
    logger.info("scan_complete", total_files=len(docx_files))

    if args.limit:
        docx_files = docx_files[:args.limit]
        logger.info("limited", limit=args.limit)

    # Initialize Neo4j driver
    driver = None
    if not args.dry_run:
        from neo4j import AsyncGraphDatabase
        driver = AsyncGraphDatabase.driver(
            args.neo4j_uri,
            auth=(args.neo4j_user, args.neo4j_password),
        )
        logger.info("neo4j_connected", uri=args.neo4j_uri)

    # Process files
    results = []
    start_time = time.time()
    loaded_count = 0
    skipped_count = 0
    error_count = 0

    for i, file_path in enumerate(docx_files):
        print(f"\n[{i+1}/{len(docx_files)}] {file_path.name}")

        if args.dry_run:
            # Just count what would happen
            skip_reason = should_skip(file_path)
            if skip_reason:
                skipped_count += 1
                print(f"   ⏭️  {skip_reason}")
            else:
                print(f"   📄 Would process")
            continue

        result = await import_file(file_path, output_dir, driver, args.batch_size)
        results.append(result)

        if result["status"] == "loaded":
            loaded_count += 1
            print(f"   ✅ Loaded: {result['nodes']} nodes, {result['rels']} rels")
        elif result["status"] == "skipped":
            skipped_count += 1
            print(f"   ⏭️  {result['error']}")
        elif result["status"] == "no_content":
            skipped_count += 1
            print(f"   📭 No content")
        else:
            error_count += 1
            print(f"   ❌ {result.get('error', 'unknown error')}")

    if driver:
        await driver.close()

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"📊 BULK IMPORT SUMMARY")
    print(f"{'='*60}")
    print(f"   Total files scanned: {len(docx_files)}")
    print(f"   ✅ Loaded:           {loaded_count}")
    print(f"   ⏭️  Skipped:         {skipped_count}")
    print(f"   ❌ Errors:           {error_count}")
    print(f"   ⏱️  Time elapsed:     {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"   📁 Output directory: {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
