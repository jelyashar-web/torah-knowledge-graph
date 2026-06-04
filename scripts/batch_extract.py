#!/usr/bin/env python3
"""
Batch extraction from Sefaria for multiple books.

Reads a list of books and extracts them sequentially with rate limiting.
Produces raw JSON + transformed Neo4j JSONL for each book.

Usage:
    uv run python scripts/batch_extract.py --books Genesis Exodus Leviticus --output data/
    uv run python scripts/batch_extract.py --phase-file data/manifests/phase1.txt --output data/
"""

import argparse
import sys
import time
from pathlib import Path

from sefaria_extractor import extract_book
from transform_for_neo4j import transform_tanakh


def extract_and_transform(book: str, data_dir: Path) -> dict:
    """Extract a book and immediately transform it."""
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"

    print(f"\n{'='*60}")
    print(f"📚 Processing: {book}")
    print(f"{'='*60}")

    # Step 1: Extract
    meta = extract_book(book, raw_dir)
    if meta.get("status") == "failed":
        return {"book": book, "status": "failed", "reason": meta.get("reason")}

    # Step 2: Transform
    safe_title = book.replace(" ", "_").replace(",", "").replace("/", "_")
    raw_file = raw_dir / f"{safe_title}.json"
    if raw_file.exists():
        transform_tanakh(raw_file, processed_dir)

    return {"book": book, "status": "success", "meta": meta}


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch extract and transform Torah texts")
    parser.add_argument("--books", nargs="+", help="List of book titles to extract")
    parser.add_argument("--phase-file", type=str, help="File with one book per line")
    parser.add_argument("--output", type=str, default="data", help="Base data directory")

    args = parser.parse_args()
    data_dir = Path(args.output)

    books: list[str] = []
    if args.books:
        books = args.books
    elif args.phase_file:
        path = Path(args.phase_file)
        if not path.exists():
            print(f"❌ Phase file not found: {path}")
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            books = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    else:
        print("❌ Please specify --books or --phase-file")
        sys.exit(1)

    print(f"🚀 Batch extraction starting: {len(books)} books")
    print(f"   Estimated time: ~{len(books) * 2} minutes (at 2 req/sec with rate limiting)")
    print()

    results = []
    start_time = time.time()

    for i, book in enumerate(books, 1):
        print(f"\n[{i}/{len(books)}] Starting {book}...")
        result = extract_and_transform(book, data_dir)
        results.append(result)

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"✅ Batch extraction complete!")
    print(f"   Books: {len(books)}")
    print(f"   Success: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"   Failed: {sum(1 for r in results if r['status'] == 'failed')}")
    print(f"   Total time: {elapsed/60:.1f} minutes")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
