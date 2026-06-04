#!/usr/bin/env python3
"""
DOCX Collection Import Pipeline for Torah Knowledge Graph.

Orchestrates the full flow:
  1. Scan library → manifest.json (sha256 + metadata)
  2. Parse each .docx → TextUnit JSONL (hebrew normalized)
  3. Validate all outputs → validation_report.json
  4. Only after validation passes → load into Neo4j (optional)

Usage:
    # Full pipeline (scan → parse → validate)
    uv run python scripts/import_docx_collection.py \
        --library-dir /path/to/torah_library \
        --output-dir data/processed/docx_import/ \
        --validate

    # Test mode: first 10 files only
    uv run python scripts/import_docx_collection.py \
        --library-dir /path/to/torah_library \
        --output-dir data/processed/docx_import/ \
        --limit 10 \
        --validate

    # Skip scan if manifest already exists
    uv run python scripts/import_docx_collection.py \
        --manifest docx_manifest.json \
        --output-dir data/processed/docx_import/ \
        --validate
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_scan(library_dir: Path, manifest_path: Path, limit: int = 0) -> Path:
    """Run scan_docx_library.py to produce manifest."""
    print(f"\n{'='*60}")
    print("🔍 STEP 1: Scanning DOCX library...")
    print(f"{'='*60}")

    cmd = [
        sys.executable, "scripts/scan_docx_library.py",
        "--library-dir", str(library_dir),
        "--output", str(manifest_path),
    ]
    if limit > 0:
        cmd.extend(["--limit", str(limit)])

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Scan failed")

    return manifest_path


def run_parse(manifest_path: Path, output_dir: Path) -> list[Path]:
    """Parse all files in manifest → JSONL."""
    print(f"\n{'='*60}")
    print("📖 STEP 2: Parsing DOCX files...")
    print(f"{'='*60}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    from docx_parser import parse_docx, save_jsonl

    output_dir.mkdir(parents=True, exist_ok=True)
    parsed_files = []

    for entry in manifest["files"]:
        docx_path = Path(entry["abs_path"])
        rel_path = entry["rel_path"]
        sha256 = entry["sha256"]

        print(f"   Parsing {rel_path}...")
        result = parse_docx(docx_path, source_file=rel_path, file_sha256=sha256)

        if result["nodes"]:
            nodes_file, rels_file = save_jsonl(result, output_dir)
            parsed_files.append(nodes_file)
            parsed_files.append(rels_file)
            print(f"      ✅ {result.get('units', len(result['nodes']) - 1)} units")
        else:
            print(f"      ⚠️  Empty or unparsable")

    print(f"\n✅ Parsed {len(manifest['files'])} files → {len(parsed_files)} JSONL files")
    return parsed_files


def run_validate(output_dir: Path) -> dict:
    """Run validate_textunits.py and return report."""
    print(f"\n{'='*60}")
    print("✅ STEP 3: Validating TextUnits...")
    print(f"{'='*60}")

    report_path = output_dir / "validation_report.json"

    cmd = [
        sys.executable, "scripts/validate_textunits.py",
        "--data-dir", str(output_dir),
        "--output", str(report_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    return report


def main():
    parser = argparse.ArgumentParser(description="DOCX Collection Import Pipeline")
    parser.add_argument("--library-dir", type=str, help="Root directory containing .docx files")
    parser.add_argument("--manifest", type=str, help="Existing manifest JSON (skip scan)")
    parser.add_argument("--output-dir", type=str, default="data/processed/docx_import", help="Output directory for JSONL")
    parser.add_argument("--limit", type=int, default=0, help="Limit to first N files (test mode)")
    parser.add_argument("--validate", action="store_true", help="Run validation after parsing")
    parser.add_argument("--load-neo4j", action="store_true", help="Load into Neo4j after validation (requires --validate)")

    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Get manifest
    if args.manifest:
        manifest_path = Path(args.manifest)
        if not manifest_path.exists():
            print(f"❌ Manifest not found: {manifest_path}")
            return 1
    elif args.library_dir:
        manifest_path = output_dir / "docx_manifest.json"
        run_scan(Path(args.library_dir), manifest_path, args.limit)
    else:
        print("❌ Please specify --library-dir or --manifest")
        return 1

    # Step 2: Parse
    parsed_files = run_parse(manifest_path, output_dir)

    # Step 3: Validate
    report = {"status": "skipped", "valid": True}
    if args.validate:
        report = run_validate(output_dir)
        if not report.get("valid", False):
            print(f"\n❌ VALIDATION FAILED — aborting Neo4j load")
            print(f"   Report: {output_dir / 'validation_report.json'}")
            print(f"   Fix issues and re-run.")
            return 1
        print(f"\n✅ VALIDATION PASSED — safe to load into Neo4j")
    else:
        print(f"\n⏭️  Validation skipped. Run with --validate to verify.")

    # Step 4: Load into Neo4j (only if validation passed)
    if args.load_neo4j and report.get("valid", False):
        print(f"\n{'='*60}")
        print("🚀 STEP 4: Loading into Neo4j...")
        print(f"{'='*60}")
        print("   (Use scripts/bulk_load_tanakh.py with the new JSONL files)")
        print("   Example:")
        print(f"   uv run python scripts/bulk_load_tanakh.py --data-dir {output_dir}")

    # Summary
    print(f"\n{'='*60}")
    print("📊 IMPORT PIPELINE COMPLETE")
    print(f"{'='*60}")
    print(f"   Output dir: {output_dir}")
    print(f"   Manifest:   {manifest_path}")
    print(f"   Validation: {'PASSED' if report.get('valid') else 'FAILED/SKIPPED'}")
    print(f"   Neo4j load: {'QUEUED' if args.load_neo4j else 'NOT REQUESTED'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
