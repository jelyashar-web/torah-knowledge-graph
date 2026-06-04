#!/usr/bin/env python3
"""
Sefaria API Extractor for Torah Knowledge Graph.

Extracts texts from Sefaria.org API with rate limiting and structured output.
Produces JSON files ready for Neo4j ingestion.

Usage:
    uv run python scripts/sefaria_extractor.py --book Genesis --output data/raw/
    uv run python scripts/sefaria_extractor.py --manifest data/manifests/torah_corpus_manifest.json --phase 1

Rate limit: 1 request per second (Sefaria requirement).
"""

import argparse
import html
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests


SEFARIA_API_BASE = "https://www.sefaria.org/api"
RATE_LIMIT_SECONDS = 1.1


def clean_html(raw: str) -> str:
    """Remove HTML tags and decode entities."""
    if not raw:
        return ""
    # Remove HTML tags
    text = re.sub(r"&lt;[^&]+&gt;", "", raw)
    text = re.sub(r"<[^>]+>", "", text)
    # Decode HTML entities
    text = html.unescape(text)
    return text.strip()


def fetch_text(ref: str, lang: str = "he", version: str | None = None) -> dict[str, Any]:
    """Fetch a text from Sefaria API."""
    url = f"{SEFARIA_API_BASE}/texts/{ref.replace(' ', '%20')}"
    params: dict[str, str] = {"lang": lang}
    if version:
        params["ven" if lang == "en" else "vhe"] = version

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_index(title: str) -> dict[str, Any]:
    """Fetch the index (metadata) for a book."""
    url = f"{SEFARIA_API_BASE}/index/{title.replace(' ', '%20')}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def get_chapter_count(index_data: dict[str, Any]) -> int:
    """Extract the number of chapters/sections from a Sefaria index."""
    schema = index_data.get("schema", {})
    lengths = schema.get("lengths", [])
    if lengths and isinstance(lengths, list) and len(lengths) > 0:
        return int(lengths[0])
    return schema.get("length", 1)


def extract_book(book_title: str, output_dir: Path, fetch_hebrew: bool = True, fetch_english: bool = True) -> dict[str, Any]:
    """Extract an entire book chapter by chapter from Sefaria.

    For Tanakh: fetches "Book Chapter" to get verse-level arrays.
    For Talmud: fetches "Book Daf" to get line-level arrays.
    """
    print(f"📖 Extracting: {book_title}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Fetch index
    print(f"   Fetching index...")
    try:
        index_data = fetch_index(book_title)
    except requests.HTTPError as e:
        print(f"   ❌ Failed to fetch index for {book_title}: {e}")
        return {"book": book_title, "status": "failed", "reason": str(e)}

    total_chapters = get_chapter_count(index_data)
    section_names = index_data.get("schema", {}).get("sectionNames", ["Chapter"])
    print(f"   {section_names[0]}s: {total_chapters}")

    book_data: dict[str, Any] = {
        "title": book_title,
        "hebrew_title": index_data.get("heTitle", ""),
        "category": index_data.get("categories", []),
        "schema": index_data.get("schema", {}),
        "refs": {},
        "extraction_meta": {
            "total_refs": total_chapters,
            "fetched_refs": 0,
            "failed_refs": 0,
            "source": "Sefaria.org",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    }

    for i in range(1, total_chapters + 1):
        ref = f"{book_title} {i}"
        ref_data: dict[str, Any] = {}

        if fetch_hebrew:
            time.sleep(RATE_LIMIT_SECONDS)
            try:
                he_data = fetch_text(ref, lang="he")
                ref_data["hebrew"] = he_data
                print(f"   [{i}/{total_chapters}] ✓ {ref} (he)")
            except requests.HTTPError as e:
                print(f"   [{i}/{total_chapters}] ✗ {ref} (he) — {e}")
                ref_data["hebrew_error"] = str(e)
                book_data["extraction_meta"]["failed_refs"] += 1

        if fetch_english:
            time.sleep(RATE_LIMIT_SECONDS)
            try:
                en_data = fetch_text(ref, lang="en")
                ref_data["english"] = en_data
                print(f"   [{i}/{total_chapters}] ✓ {ref} (en)")
            except requests.HTTPError as e:
                print(f"   [{i}/{total_chapters}] ✗ {ref} (en) — {e}")
                ref_data["english_error"] = str(e)
                book_data["extraction_meta"]["failed_refs"] += 1

        book_data["refs"][ref] = ref_data
        book_data["extraction_meta"]["fetched_refs"] += 1

    # Save
    safe_title = book_title.replace(" ", "_").replace(",", "").replace("/", "_")
    output_file = output_dir / f"{safe_title}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(book_data, f, ensure_ascii=False, indent=2)

    print(f"   💾 Saved to {output_file}")
    print(f"   📊 Fetched: {book_data['extraction_meta']['fetched_refs']}, Failed: {book_data['extraction_meta']['failed_refs']}")

    return book_data["extraction_meta"]


def extract_from_manifest(manifest_path: Path, output_dir: Path, phase: int | None = None) -> None:
    """Extract books listed in a manifest JSON file."""
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    if phase is not None:
        phase_key = f"phase_{phase}"
        if phase_key not in manifest.get("extraction_plan", {}):
            print(f"❌ Phase {phase} not found in manifest")
            sys.exit(1)
        books = manifest["extraction_plan"][phase_key]["books"]
        print(f"🚀 Extracting Phase {phase}: {manifest['extraction_plan'][phase_key]['description']}")
    else:
        books = []
        for cat, info in manifest.get("categories", {}).items():
            if info.get("priority") == 1:
                books.extend(info.get("books", []))
        print(f"🚀 Extracting all priority-1 books ({len(books)} books)")

    results: list[dict[str, Any]] = []
    for book in books:
        meta = extract_book(book, output_dir)
        results.append(meta)

    report = {
        "manifest": str(manifest_path),
        "phase": phase,
        "output_dir": str(output_dir),
        "results": results,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    report_file = output_dir / "_extraction_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n📋 Extraction report saved to {report_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Torah texts from Sefaria API")
    parser.add_argument("--book", type=str, help="Extract a single book (e.g., 'Genesis')")
    parser.add_argument("--manifest", type=str, help="Path to manifest JSON")
    parser.add_argument("--phase", type=int, help="Extract only books from this phase (requires --manifest)")
    parser.add_argument("--output", type=str, default="data/raw", help="Output directory")
    parser.add_argument("--no-hebrew", action="store_true", help="Skip Hebrew text")
    parser.add_argument("--no-english", action="store_true", help="Skip English text")

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.book:
        extract_book(
            args.book,
            output_dir,
            fetch_hebrew=not args.no_hebrew,
            fetch_english=not args.no_english,
        )
    elif args.manifest:
        extract_from_manifest(Path(args.manifest), output_dir, args.phase)
    else:
        print("❌ Please specify --book or --manifest")
        sys.exit(1)


if __name__ == "__main__":
    main()
