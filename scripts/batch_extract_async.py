#!/usr/bin/env python3
"""
Async batch extraction from Sefaria using aiohttp.
Runs multiple requests concurrently with rate limiting.

Usage:
    uv run python scripts/batch_extract_async.py --phase-file data/manifests/phase2_mishnah.txt
    nohup uv run python scripts/batch_extract_async.py --all-phases --skip-existing > extraction.log 2>&1 &
"""

import argparse
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

import aiohttp
import aiofiles

# ── Config ──────────────────────────────────────────────
RATE_LIMIT = 1.0  # seconds between requests (polite)
CONCURRENCY = 3   # max concurrent requests
API_BASE = "https://www.sefaria.org/api"


# ── Fetch single book ───────────────────────────────────

async def fetch_book(session: aiohttp.ClientSession, book: str, raw_dir: Path) -> dict:
    """Fetch a single book from Sefaria."""
    safe_title = book.replace(" ", "_").replace(",", "").replace("/", "_")
    raw_file = raw_dir / f"{safe_title}.json"

    # Check if already exists
    if raw_file.exists():
        return {"book": book, "status": "skipped", "reason": "already exists"}

    # Try text API
    url = f"{API_BASE}/texts/{book}"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
            if resp.status == 200:
                data = await resp.json()
                async with aiofiles.open(raw_file, "w", encoding="utf-8") as f:
                    await f.write(json.dumps(data, indent=2, ensure_ascii=False))
                return {
                    "book": book,
                    "status": "success",
                    "verses": len(str(data)),
                }
            elif resp.status == 404:
                return {"book": book, "status": "failed", "reason": "not found"}
            else:
                return {"book": book, "status": "failed", "reason": f"HTTP {resp.status}"}
    except Exception as e:
        return {"book": book, "status": "failed", "reason": str(e)}


# ── Semaphore-guarded fetch ─────────────────────────────

async def fetch_with_limit(session: aiohttp.ClientSession, book: str, raw_dir: Path, sem: asyncio.Semaphore, delay: float) -> dict:
    """Fetch with concurrency limit and rate delay."""
    async with sem:
        result = await fetch_book(session, book, raw_dir)
        await asyncio.sleep(delay)
        return result


# ── Batch runner ────────────────────────────────────────

async def run_batch(books: list[str], raw_dir: Path, skip_existing: bool = True) -> list[dict]:
    """Run batch extraction with controlled concurrency."""
    raw_dir.mkdir(parents=True, exist_ok=True)

    if skip_existing:
        existing = {f.stem.replace("_", " ") for f in raw_dir.glob("*.json")}
        books = [b for b in books if b not in existing]
        print(f"🔍 Skipping {len(existing)} existing, extracting {len(books)} new")

    if not books:
        print("✅ All books already extracted!")
        return []

    print(f"🚀 Starting async extraction: {len(books)} books, concurrency={CONCURRENCY}")
    print(f"   Estimated time: ~{len(books) * RATE_LIMIT / CONCURRENCY:.0f} minutes")

    sem = asyncio.Semaphore(CONCURRENCY)
    start = time.time()
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_limit(session, book, raw_dir, sem, RATE_LIMIT) for book in books]

        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            results.append(result)
            status_emoji = "✅" if result["status"] == "success" else ("⏭️" if result["status"] == "skipped" else "❌")
            print(f"  [{len(results)}/{len(books)}] {status_emoji} {result['book']}")

    elapsed = time.time() - start
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "failed")
    skipped = sum(1 for r in results if r["status"] == "skipped")

    print(f"\n{'=' * 60}")
    print(f"✅ Batch complete!")
    print(f"   Total: {len(results)}")
    print(f"   Success: {success}")
    print(f"   Failed: {failed}")
    print(f"   Skipped: {skipped}")
    print(f"   Time: {elapsed / 60:.1f} minutes")
    print(f"   Rate: {len(results) / elapsed:.1f} books/sec")
    print(f"{'=' * 60}")

    return results


# ── Phase file parsing ──────────────────────────────────

def parse_phase_file(path: Path) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]


# ── Main ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Async batch extraction from Sefaria")
    parser.add_argument("--books", nargs="+", help="List of book titles")
    parser.add_argument("--phase-file", type=str, help="Phase file with book list")
    parser.add_argument("--all-phases", action="store_true", help="Extract all phase files")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="Skip existing files")
    parser.add_argument("--output", type=str, default="data", help="Output directory")

    args = parser.parse_args()
    raw_dir = Path(args.output) / "raw"

    books = []
    if args.books:
        books = args.books
    elif args.phase_file:
        books = parse_phase_file(Path(args.phase_file))
    elif args.all_phases:
        manifests_dir = Path(args.output) / "manifests"
        for pf in sorted(manifests_dir.glob("phase*.txt")):
            books.extend(parse_phase_file(pf))
    else:
        print("❌ Specify --books, --phase-file, or --all-phases")
        return

    asyncio.run(run_batch(books, raw_dir, skip_existing=args.skip_existing))


if __name__ == "__main__":
    main()
