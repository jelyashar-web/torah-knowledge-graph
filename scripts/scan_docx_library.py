#!/usr/bin/env python3
"""
Recursively scan a directory tree for .docx files and produce a manifest
with SHA-256 hashes, file sizes, and detected metadata.

Usage:
    uv run python scripts/scan_docx_library.py --library-dir /path/to/torah_library --output docx_manifest.json
"""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def detect_docx_metadata(docx_path: Path) -> dict:
    """Quick metadata extraction from a .docx file."""
    try:
        import docx
        doc = docx.Document(docx_path)
        # Count paragraphs
        para_count = len(doc.paragraphs)
        # Count text runs (approximate word count)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        word_count = len(text.split())
        char_count = len(text)
        return {
            "paragraphs": para_count,
            "words_estimate": word_count,
            "chars_estimate": char_count,
        }
    except Exception:
        return {"paragraphs": 0, "words_estimate": 0, "chars_estimate": 0}


def scan_library(library_dir: Path) -> list[dict]:
    """Recursively scan for .docx files and build manifest."""
    entries = []
    docx_files = sorted(library_dir.rglob("*.docx"))

    for idx, docx_file in enumerate(docx_files, 1):
        rel_path = docx_file.relative_to(library_dir)
        print(f"  [{idx}/{len(docx_files)}] Scanning {rel_path}...")

        stats = docx_file.stat()
        metadata = detect_docx_metadata(docx_file)

        entry = {
            "abs_path": str(docx_file),
            "rel_path": str(rel_path),
            "filename": docx_file.name,
            "sha256": sha256_file(docx_file),
            "size_bytes": stats.st_size,
            "modified": datetime.fromtimestamp(stats.st_mtime, tz=timezone.utc).isoformat(),
            "paragraphs": metadata["paragraphs"],
            "words_estimate": metadata["words_estimate"],
            "chars_estimate": metadata["chars_estimate"],
        }
        entries.append(entry)

    return entries


def main():
    parser = argparse.ArgumentParser(description="Scan .docx Torah library")
    parser.add_argument("--library-dir", type=str, required=True, help="Root directory to scan recursively")
    parser.add_argument("--output", type=str, default="docx_manifest.json", help="Output manifest JSON file")
    parser.add_argument("--limit", type=int, default=0, help="Limit to first N files (0 = no limit)")

    args = parser.parse_args()
    library_dir = Path(args.library_dir)

    if not library_dir.exists():
        print(f"❌ Directory not found: {library_dir}")
        return 1

    print(f"🔍 Scanning {library_dir} for .docx files...")
    entries = scan_library(library_dir)

    if args.limit > 0:
        entries = entries[:args.limit]
        print(f"📋 Limited to first {args.limit} files")

    total_size = sum(e["size_bytes"] for e in entries)

    manifest = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "library_dir": str(library_dir),
        "total_files": len(entries),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "files": entries,
    }

    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Manifest saved: {output_path}")
    print(f"   Files: {len(entries)}")
    print(f"   Total size: {manifest['total_size_mb']:.2f} MB")
    print(f"   SHA-256 hashes: {len(entries)} calculated")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
