#!/usr/bin/env python3
"""
Transform Sefaria raw JSON into Neo4j-ready JSONL.

Converts extracted Sefaria texts into a format ready for Neo4j bulk import.
Produces:
  - {book}_nodes.jsonl (all Verse, Chapter, Book nodes)
  - {book}_relationships.jsonl (all PART_OF relationships)

Usage:
    uv run python scripts/transform_for_neo4j.py --input data/raw/Genesis.json --output data/processed/
"""

import argparse
import html
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any

from hebrew_utils import normalize_hebrew


def generate_uuid() -> str:
    """Generate a UUID for Neo4j nodes."""
    return str(uuid.uuid4())


def clean_text(raw: str) -> str:
    """Remove HTML tags and decode entities from Sefaria text."""
    if not raw:
        return ""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", raw)
    # Decode HTML entities
    text = html.unescape(text)
    return text.strip()


def parse_ref(ref: str) -> dict[str, Any]:
    """Parse a Sefaria reference into structured components."""
    # Try "Book Chapter:Verse"
    match = re.match(r"^(.+?)\s+(\d+):(\d+)$", ref)
    if match:
        return {
            "book": match.group(1),
            "chapter": int(match.group(2)),
            "verse": int(match.group(3)),
            "ref": ref,
        }
    # Try "Book Chapter"
    match = re.match(r"^(.+?)\s+(\d+)$", ref)
    if match:
        return {
            "book": match.group(1),
            "chapter": int(match.group(2)),
            "ref": ref,
        }
    return {"book": ref, "ref": ref}


def extract_verses_from_chapter(chapter_data: dict[str, Any]) -> list[dict[str, str]]:
    """Extract verse-level Hebrew and English from a chapter response.

    Sefaria chapter responses have:
      - he: array of verse strings (Hebrew)
      - text: array of verse strings (English)
    """
    verses: list[dict[str, str]] = []

    he_verses = chapter_data.get("he", [])
    en_verses = chapter_data.get("text", [])

    # Handle nested arrays (some texts have double nesting)
    def flatten_verses(t: Any) -> list[str]:
        result: list[str] = []
        if isinstance(t, list):
            for item in t:
                result.extend(flatten_verses(item))
        elif isinstance(t, str):
            result.append(t)
        return result

    he_flat = flatten_verses(he_verses)
    en_flat = flatten_verses(en_verses)

    max_verses = max(len(he_flat), len(en_flat))
    for i in range(max_verses):
        verses.append({
            "hebrew": clean_text(he_flat[i]) if i < len(he_flat) else "",
            "english": clean_text(en_flat[i]) if i < len(en_flat) else "",
            "verse_number": i + 1,
        })

    return verses


def transform_tanakh(raw_file: Path, output_dir: Path) -> dict[str, Any]:
    """Transform a raw Sefaria Tanakh JSON into Neo4j-ready JSONL."""
    print(f"🔄 Transforming: {raw_file.name}")

    with open(raw_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    book_title = data.get("title", "Unknown")
    hebrew_title = data.get("hebrew_title", "")
    category = data.get("category", ["Tanakh"])
    refs = data.get("refs", {})

    nodes: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []

    # Book node
    book_id = generate_uuid()
    nodes.append({
        "id": book_id,
        "label": "Book",
        "properties": {
            "title": book_title,
            "hebrew_title": hebrew_title,
            "category": category[0] if category else "Tanakh",
            "corpus": category[0] if category else "Tanakh",
            "canonical": True,
            "is_commentary": False,
        },
    })

    # Process each chapter
    for ref, ref_data in sorted(refs.items(), key=lambda x: parse_ref(x[0]).get("chapter", 0)):
        parsed = parse_ref(ref)
        chapter_num = parsed.get("chapter", 0)
        if chapter_num == 0:
            continue

        # Chapter node
        chapter_id = generate_uuid()
        nodes.append({
            "id": chapter_id,
            "label": "Chapter",
            "properties": {
                "ref": ref,
                "book": book_title,
                "hebrew_book": hebrew_title,
                "number": chapter_num,
                "category": category[0] if category else "Tanakh",
                "corpus": category[0] if category else "Tanakh",
            },
        })

        # Chapter -> Book
        relationships.append({
            "type": "PART_OF",
            "from_id": chapter_id,
            "to_id": book_id,
            "properties": {
                "part_type": "chapter_of_book",
                "order_index": chapter_num,
                "confidence": 1.0,
                "source": "canonical",
                "extraction_method": "imported",
            },
        })

        # Extract verses from Hebrew chapter data
        hebrew_chapter = ref_data.get("hebrew", {})
        verses = extract_verses_from_chapter(hebrew_chapter)

        for v in verses:
            verse_num = v["verse_number"]
            verse_ref = f"{book_title} {chapter_num}:{verse_num}"

            verse_id = generate_uuid()
            nodes.append({
                "id": verse_id,
                "label": "Verse",
                "properties": {
                    "ref": verse_ref,
                    "book": book_title,
                    "hebrew_book": hebrew_title,
                    "chapter": chapter_num,
                    "verse_number": verse_num,
                    "text_hebrew": v["hebrew"],
                    "text_hebrew_normalized": normalize_hebrew(v["hebrew"]),
                    "text_english": v["english"],
                    "language": "hebrew",
                    "category": category[0] if category else "Tanakh",
                    "corpus": category[0] if category else "Tanakh",
                    "canonical": True,
                    "sefaria_ref": verse_ref,
                },
            })

            # Verse -> Chapter
            relationships.append({
                "type": "PART_OF",
                "from_id": verse_id,
                "to_id": chapter_id,
                "properties": {
                    "part_type": "verse_of_chapter",
                    "order_index": verse_num,
                    "confidence": 1.0,
                    "source": "canonical",
                    "extraction_method": "imported",
                },
            })

    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = raw_file.stem
    nodes_file = output_dir / f"{safe_name}_nodes.jsonl"
    with open(nodes_file, "w", encoding="utf-8") as f:
        for node in nodes:
            f.write(json.dumps(node, ensure_ascii=False) + "\n")

    rels_file = output_dir / f"{safe_name}_relationships.jsonl"
    with open(rels_file, "w", encoding="utf-8") as f:
        for rel in relationships:
            f.write(json.dumps(rel, ensure_ascii=False) + "\n")

    print(f"   💾 Nodes: {len(nodes)} → {nodes_file}")
    print(f"   💾 Relationships: {len(relationships)} → {rels_file}")

    return {
        "book": book_title,
        "nodes": len(nodes),
        "relationships": len(relationships),
        "nodes_file": str(nodes_file),
        "relationships_file": str(rels_file),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Transform Sefaria raw JSON to Neo4j-ready JSONL")
    parser.add_argument("--input", type=str, required=True, help="Raw Sefaria JSON file")
    parser.add_argument("--output", type=str, default="data/processed", help="Output directory")

    args = parser.parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output)

    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        sys.exit(1)

    result = transform_tanakh(input_path, output_dir)
    print(f"\n✅ Transformation complete: {result['book']}")
    print(f"   Nodes: {result['nodes']}, Relationships: {result['relationships']}")


if __name__ == "__main__":
    main()
