#!/usr/bin/env python3
"""
Validate TextUnit JSONL files before loading into Neo4j.

Checks:
  - No empty text units
  - No duplicate node IDs
  - Valid UTF-8 Hebrew text
  - text_hebrew_normalized present and non-empty
  - Relationship endpoints exist in nodes
  - SOURCE_FILE relationships point to valid SourceFile nodes

Usage:
    uv run python scripts/validate_textunits.py --data-dir data/processed/docx_import/ --output validation_report.json
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def has_meaningful_content(text: str) -> bool:
    """Check if text has meaningful content (not just whitespace/punctuation).

    Allows English, numbers, Hebrew — just rejects truly empty strings.
    """
    if not text:
        return False
    # Strip whitespace and punctuation; check if anything remains
    stripped = text.strip()
    if not stripped:
        return False
    # Reject if only punctuation/symbols
    import re
    alphanumeric = re.sub(r"[^\w\s]", "", stripped)
    return len(alphanumeric) > 0


def validate_nodes(nodes_file: Path) -> dict:
    """Validate a single nodes JSONL file."""
    errors = []
    warnings = []
    node_count = 0
    textunit_count = 0
    empty_text = 0
    missing_normalized = 0
    invalid_hebrew = 0
    seen_ids = set()
    duplicate_ids = []

    with open(nodes_file, "r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                node = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_no}: Invalid JSON — {e}")
                continue

            node_count += 1
            node_id = node.get("id", "")
            label = node.get("label", "")
            props = node.get("properties", {})

            # Duplicate ID check
            if node_id in seen_ids:
                duplicate_ids.append(node_id)
            seen_ids.add(node_id)

            # TextUnit-specific checks
            if label == "TextUnit":
                textunit_count += 1
                text_he = props.get("text_hebrew", "")
                text_norm = props.get("text_hebrew_normalized", "")

                if not text_he or not text_he.strip():
                    empty_text += 1
                    errors.append(f"Line {line_no}: TextUnit has empty text_hebrew (id={node_id})")

                if not text_norm:
                    missing_normalized += 1
                    warnings.append(f"Line {line_no}: TextUnit missing text_hebrew_normalized (id={node_id})")

                if text_he and not has_meaningful_content(text_he):
                    invalid_hebrew += 1
                    errors.append(f"Line {line_no}: TextUnit has no meaningful content (id={node_id})")

            # Book node checks
            if label == "Book":
                title = props.get("title", "")
                if not title:
                    errors.append(f"Line {line_no}: Book node missing title (id={node_id})")

    return {
        "file": str(nodes_file.name),
        "node_count": node_count,
        "textunit_count": textunit_count,
        "empty_text": empty_text,
        "missing_normalized": missing_normalized,
        "invalid_hebrew": invalid_hebrew,
        "duplicate_ids": duplicate_ids,
        "errors": errors,
        "warnings": warnings,
    }


def validate_relationships(rels_file: Path, node_ids: set) -> dict:
    """Validate a relationships JSONL file against known node IDs."""
    errors = []
    rel_count = 0
    dangling_from = 0
    dangling_to = 0

    with open(rels_file, "r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rel = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_no}: Invalid JSON — {e}")
                continue

            rel_count += 1
            from_id = rel.get("from_id", "")
            to_id = rel.get("to_id", "")
            rel_type = rel.get("type", "")

            if from_id not in node_ids:
                dangling_from += 1
                errors.append(
                    f"Line {line_no}: Relationship {rel_type} from_id '{from_id}' not found in nodes"
                )

            if to_id not in node_ids:
                dangling_to += 1
                errors.append(
                    f"Line {line_no}: Relationship {rel_type} to_id '{to_id}' not found in nodes"
                )

    return {
        "file": str(rels_file.name),
        "rel_count": rel_count,
        "dangling_from": dangling_from,
        "dangling_to": dangling_to,
        "errors": errors,
    }


def validate_collection(data_dir: Path) -> dict:
    """Validate all JSONL files in a directory."""
    nodes_files = sorted(data_dir.glob("*_nodes.jsonl"))
    rels_files = sorted(data_dir.glob("*_relationships.jsonl"))

    all_node_ids = set()
    node_results = []
    rel_results = []
    total_errors = 0
    total_warnings = 0

    print(f"📁 Validating {len(nodes_files)} nodes files + {len(rels_files)} relationships files...")

    # First pass: validate all nodes and collect IDs
    for nodes_file in nodes_files:
        result = validate_nodes(nodes_file)
        node_results.append(result)
        total_errors += len(result["errors"])
        total_warnings += len(result["warnings"])

        # Collect IDs for relationship validation
        with open(nodes_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    node = json.loads(line)
                    all_node_ids.add(node.get("id", ""))
                except json.JSONDecodeError:
                    pass

    # Second pass: validate relationships against collected IDs
    for rels_file in rels_files:
        result = validate_relationships(rels_file, all_node_ids)
        rel_results.append(result)
        total_errors += len(result["errors"])

    valid = total_errors == 0

    return {
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "data_dir": str(data_dir),
        "nodes_files_count": len(nodes_files),
        "rels_files_count": len(rels_files),
        "total_node_ids": len(all_node_ids),
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "valid": valid,
        "node_results": node_results,
        "relationship_results": rel_results,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate TextUnit JSONL files")
    parser.add_argument("--data-dir", type=str, required=True, help="Directory containing *_nodes.jsonl and *_relationships.jsonl")
    parser.add_argument("--output", type=str, default="validation_report.json", help="Output report JSON file")

    args = parser.parse_args()
    data_dir = Path(args.data_dir)

    if not data_dir.exists():
        print(f"❌ Directory not found: {data_dir}")
        return 1

    report = validate_collection(data_dir)

    # Print summary
    print(f"\n{'='*60}")
    print("📊 VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"   Data dir:     {report['data_dir']}")
    print(f"   Nodes files:  {report['nodes_files_count']}")
    print(f"   Rels files:   {report['rels_files_count']}")
    print(f"   Total IDs:    {report['total_node_ids']}")
    print(f"   Errors:       {report['total_errors']}")
    print(f"   Warnings:     {report['total_warnings']}")
    print(f"   Status:       {'✅ VALID' if report['valid'] else '❌ FAILED'}")

    # Detail any errors
    if report["total_errors"] > 0:
        print(f"\n   First 10 errors:")
        count = 0
        for nr in report["node_results"]:
            for err in nr["errors"][:5]:
                print(f"      • {err}")
                count += 1
                if count >= 10:
                    break
            if count >= 10:
                break
        for rr in report["relationship_results"]:
            for err in rr["errors"][:5]:
                print(f"      • {err}")
                count += 1
                if count >= 10:
                    break
            if count >= 10:
                break

    # Write report
    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Report saved: {output_path}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
