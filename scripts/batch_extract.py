#!/usr/bin/env python3
"""
Batch extraction from Sefaria for multiple books.

Supports:
- Resume: skips books already present in data/raw/
- Progress tracking
- Phase-by-phase execution
- Dry-run mode

Usage:
    # Extract specific books
    uv run python scripts/batch_extract.py --books Genesis Exodus

    # Extract from phase file (skips existing)
    uv run python scripts/batch_extract.py --phase-file data/manifests/phase2_mishnah.txt

    # Extract all phases, skip existing
    uv run python scripts/batch_extract.py --all-phases --skip-existing

    # Dry run: see what WOULD be extracted
    uv run python scripts/batch_extract.py --all-phases --skip-existing --dry-run

    # Full extraction (background)
    nohup uv run python scripts/batch_extract.py --all-phases --skip-existing > extraction.log 2>&1 &
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sefaria_extractor import extract_book
from transform_for_neo4j import transform_tanakh


def get_all_phase_files(manifests_dir: Path) -> List[Path]:
    """Return all phase files sorted by name."""
    files = sorted(manifests_dir.glob("phase*.txt"))
    return [f for f in files if "_torah" not in f.name or "phase1" in f.name]


def parse_phase_file(path: Path) -> List[str]:
    """Read book names from a phase file (skip comments and empty lines)."""
    with open(path, "r", encoding="utf-8") as f:
        books = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]
    return books


def get_existing_books(raw_dir: Path) -> set:
    """Return set of book titles already extracted (from JSON filenames)."""
    existing = set()
    for f in raw_dir.glob("*.json"):
        # Convert filename back to book title
        title = f.stem.replace("_", " ")
        existing.add(title)
    return existing


def extract_and_transform(
    book: str,
    data_dir: Path,
    force: bool = False,
    dry_run: bool = False,
) -> Dict:
    """Extract a book and immediately transform it."""
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"

    safe_title = book.replace(" ", "_").replace(",", "").replace("/", "_")
    raw_file = raw_dir / f"{safe_title}.json"

    if not force and raw_file.exists():
        return {
            "book": book,
            "status": "skipped",
            "reason": f"Already exists: {raw_file}",
        }

    if dry_run:
        return {"book": book, "status": "dry_run"}

    print(f"\n{'=' * 60}")
    print(f"📚 Processing: {book}")
    print(f"{'=' * 60}")

    # Step 1: Extract
    meta = extract_book(book, raw_dir)
    if meta.get("status") == "failed":
        return {"book": book, "status": "failed", "reason": meta.get("reason")}

    # Step 2: Transform
    if raw_file.exists():
        transform_tanakh(raw_file, processed_dir)

    return {"book": book, "status": "success", "meta": meta}


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch extract and transform Torah texts")
    parser.add_argument("--books", nargs="+", help="List of book titles to extract")
    parser.add_argument("--phase-file", type=str, help="File with one book per line")
    parser.add_argument("--all-phases", action="store_true", help="Extract all phase files")
    parser.add_argument("--skip-existing", action="store_true", help="Skip books already in data/raw/")
    parser.add_argument("--force", action="store_true", help="Re-extract even if file exists")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be extracted without doing it")
    parser.add_argument("--output", type=str, default="data", help="Base data directory")
    parser.add_argument("--resume-log", type=str, default="data/extraction_progress.json", help="Progress tracking file")

    args = parser.parse_args()
    data_dir = Path(args.output)
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Gather books to extract
    books: List[str] = []
    phase_names: List[str] = []

    if args.books:
        books = args.books
    elif args.phase_file:
        path = Path(args.phase_file)
        if not path.exists():
            print(f"❌ Phase file not found: {path}")
            sys.exit(1)
        books = parse_phase_file(path)
        phase_names = [path.name]
    elif args.all_phases:
        manifests_dir = data_dir / "manifests"
        phase_files = get_all_phase_files(manifests_dir)
        for pf in phase_files:
            phase_books = parse_phase_file(pf)
            books.extend(phase_books)
            phase_names.append(pf.name)
    else:
        print("❌ Please specify --books, --phase-file, or --all-phases")
        sys.exit(1)

    # Check existing
    existing = get_existing_books(raw_dir) if args.skip_existing else set()
    if existing and args.skip_existing:
        print(f"🔍 Found {len(existing)} existing books in {raw_dir}")

    to_extract = []
    for book in books:
        if args.skip_existing and book in existing:
            continue
        to_extract.append(book)

    if not to_extract:
        print("✅ All books already extracted!")
        return

    if args.dry_run:
        print(f"\n🧪 DRY RUN — Would extract {len(to_extract)} books:")
        for b in to_extract:
            print(f"   • {b}")
        print(f"\n   Estimated time: ~{len(to_extract) * 1.5:.0f} minutes")
        return

    print(f"\n🚀 Batch extraction starting: {len(to_extract)} books")
    if phase_names:
        print(f"   Phases: {', '.join(phase_names)}")
    print(f"   Output: {data_dir.absolute()}")
    print(f"   Skip existing: {args.skip_existing}")
    print(f"   Estimated time: ~{len(to_extract) * 1.5:.0f} minutes")
    print()

    results = []
    start_time = time.time()
    progress_log = {"start_time": datetime.now().isoformat(), "books": []}

    for i, book in enumerate(to_extract, 1):
        print(f"\n[{i}/{len(to_extract)}] Starting {book}...")
        result = extract_and_transform(book, data_dir, force=args.force, dry_run=args.dry_run)
        results.append(result)
        progress_log["books"].append({
            "book": book,
            "status": result["status"],
            "timestamp": datetime.now().isoformat(),
        })

        # Save progress every 10 books
        if i % 10 == 0:
            with open(args.resume_log, "w", encoding="utf-8") as f:
                json.dump(progress_log, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start_time
    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = sum(1 for r in results if r["status"] == "failed")
    skipped_count = sum(1 for r in results if r["status"] == "skipped")

    # Final progress log
    progress_log["end_time"] = datetime.now().isoformat()
    progress_log["summary"] = {
        "total": len(to_extract),
        "success": success_count,
        "failed": failed_count,
        "skipped": skipped_count,
        "elapsed_minutes": round(elapsed / 60, 1),
    }
    with open(args.resume_log, "w", encoding="utf-8") as f:
        json.dump(progress_log, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"✅ Batch extraction complete!")
    print(f"   Books: {len(to_extract)}")
    print(f"   Success: {success_count}")
    print(f"   Failed: {failed_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Total time: {elapsed / 60:.1f} minutes")
    print(f"   Log saved to: {args.resume_log}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
