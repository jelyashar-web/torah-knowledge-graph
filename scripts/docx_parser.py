#!/usr/bin/env python3
"""
Parser for .docx Torah texts from Torat Emet collection.

Extracts structured text from Word documents and produces Neo4j-ready JSONL.
Handles:
  - Chumash (chapter:verse structure)
  - Nach (chapter:verse structure)
  - Talmud (daf:amud structure)
  - Free-form texts (paragraph chunking with heading detection)

Usage:
    uv run python scripts/docx_parser.py --input /path/to/file.docx --output data/processed/
    uv run python scripts/docx_parser.py --dir /path/to/category/ --output data/processed/
"""

import argparse
import hashlib
import json
import re
import uuid
from pathlib import Path
from typing import Any


def book_uuid(title: str) -> str:
    """Generate a deterministic UUID for a Book node based on its title.

    This ensures the same book always gets the same UUID,
    so apoc.merge.node can correctly merge without constraint violations.
    """
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"book.{title}"))

try:
    import structlog
    _logger = structlog.get_logger()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    _logger = logging.getLogger("docx_parser")

class _SimpleLogger:
    """Wrapper to make stdlib logging accept kwargs like structlog."""
    def __init__(self, logger):
        self._logger = logger
    def info(self, msg, **kwargs):
        self._logger.info(msg + " | " + " ".join(f"{k}={v}" for k, v in kwargs.items()))
    def warning(self, msg, **kwargs):
        self._logger.warning(msg + " | " + " ".join(f"{k}={v}" for k, v in kwargs.items()))
    def error(self, msg, **kwargs):
        self._logger.error(msg + " | " + " ".join(f"{k}={v}" for k, v in kwargs.items()))

if hasattr(_logger, "bind"):
    logger = _logger
else:
    logger = _SimpleLogger(_logger)

try:
    import docx
except ImportError:
    raise ImportError("Install python-docx: pip install python-docx")

# Hebrew numerals for chapter detection
HEBREW_NUMERALS = "אבגדהוזחטיכלמנסעפצקרשת"
HEBREW_NUMERAL_MAP = {c: i + 1 for i, c in enumerate(HEBREW_NUMERALS)}


def hebrew_to_int(hebrew: str) -> int:
    """Convert Hebrew numeral string to integer."""
    total = 0
    for c in hebrew:
        if c in HEBREW_NUMERAL_MAP:
            total += HEBREW_NUMERAL_MAP[c]
    return total


def clean_text(text: str) -> str:
    """Clean extracted text."""
    # Remove multiple spaces
    text = re.sub(r" +", " ", text)
    # Remove zero-width chars
    text = text.replace("​", "").replace("‎", "").replace("‏", "")
    # Normalize RTL markers
    text = re.sub(r"[‪-‮]", "", text)
    return text.strip()


def detect_structure(paragraphs: list[str]) -> str:
    """Detect document structure type."""
    # Check for chapter:verse patterns
    verse_pattern = re.compile(r"[א-ת]+\s*[\-\.:]\s*\d+")
    chapter_pattern = re.compile(r"פרק\s+[א-ת]+|\d+")

    verse_hits = sum(1 for p in paragraphs if verse_pattern.search(p))
    chapter_hits = sum(1 for p in paragraphs if chapter_pattern.search(p))

    total = len(paragraphs)
    if verse_hits / total > 0.3:
        return "verse_by_verse"
    if chapter_hits / total > 0.1:
        return "chapter_based"
    return "free_form"


def extract_docx_text(docx_path: Path) -> list[dict[str, Any]]:
    """Extract paragraphs with style info from .docx."""
    doc = docx.Document(docx_path)
    paragraphs = []
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue
        style = para.style.name if para.style else "Normal"
        is_bold = any(run.bold for run in para.runs if run.bold)
        is_heading = style.startswith("Heading") or "כותרת" in style or is_bold
        paragraphs.append({
            "index": i,
            "text": clean_text(text),
            "style": style,
            "is_heading": is_heading,
            "is_bold": is_bold,
        })
    return paragraphs


def parse_chumash(paragraphs: list[dict[str, Any]], book_title: str) -> dict[str, Any]:
    """Parse Chumash with chapter:verse structure from Torat Emet .docx.

    Structure:
      - Chapter headers: "בראשית פרק-ב"
      - Verse markers: "{א} בְּרֵאשִׁית בָּרָא..." followed by translations
    """
    nodes: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []

    book_id = book_uuid(book_title)
    nodes.append({
        "id": book_id,
        "label": "Book",
        "properties": {
            "title": book_title,
            "hebrew_title": "",
            "category": "Tanakh",
            "corpus": "Torat_Emet_Collection",
            "canonical": True,
            "source": "Torat Emet",
            "license": "CC BY-NC-SA 2.5",
        },
    })

    current_chapter = 0
    current_chapter_id = None

    # Patterns for Torat Emet Chumash format
    # Chapter: "בראשית פרק-ב" (book title + " פרק-" + number)
    chapter_pattern = re.compile(rf"^{re.escape(book_title)}\s+פרק\s*[-–]\s*([א-ת0-9]+)")
    # Verse marker: "{א} ..." or "{ב} ..."
    verse_pattern = re.compile(r"^\s*\{([א-ת]+)\}\s*(.+)$")
    # Split translations: Hebrew text ends before "אונקלוס" or "יונתן"
    translation_split = re.compile(r"\s+אונקלוס\s+|\s+יונתן\s+")

    for para in paragraphs:
        text = para["text"]
        if not text:
            continue

        # Skip license/attribution paragraphs
        if "תורת אמת" in text and ("רשיון" in text or "זכויות" in text):
            continue

        # Check for chapter heading
        ch_match = chapter_pattern.match(text)
        if ch_match:
            heb_num = ch_match.group(1)
            try:
                current_chapter = hebrew_to_int(heb_num)
            except Exception:
                # Try plain integer
                try:
                    current_chapter = int(heb_num)
                except ValueError:
                    continue
            current_chapter_id = str(uuid.uuid4())
            nodes.append({
                "id": current_chapter_id,
                "label": "Chapter",
                "properties": {
                    "ref": f"{book_title} {current_chapter}",
                    "book": book_title,
                    "number": current_chapter,
                    "category": "Tanakh",
                    "corpus": "Torat_Emet_Collection",
                },
            })
            relationships.append({
                "type": "PART_OF",
                "from_id": current_chapter_id,
                "to_id": book_id,
                "properties": {
                    "part_type": "chapter_of_book",
                    "order_index": current_chapter,
                    "confidence": 1.0,
                    "source": "Torat Emet",
                    "extraction_method": "docx_parser",
                },
            })
            continue

        # Check for verse
        if current_chapter_id:
            v_match = verse_pattern.match(text)
            if v_match:
                heb_verse = v_match.group(1)
                verse_text_raw = v_match.group(2)
                try:
                    verse_num = hebrew_to_int(heb_verse)
                except Exception:
                    verse_num = 0

                # Extract only the Hebrew text, remove translations
                verse_text = translation_split.split(verse_text_raw)[0]
                # Clean up any remaining translation prefixes
                verse_text = re.sub(r"\s+יונתן\s+.*$", "", verse_text)
                verse_text = re.sub(r"\s+אונקלוס\s+.*$", "", verse_text)
                verse_text = verse_text.strip()

                verse_id = str(uuid.uuid4())
                ref = f"{book_title} {current_chapter}:{verse_num}"
                nodes.append({
                    "id": verse_id,
                    "label": "Verse",
                    "properties": {
                        "ref": ref,
                        "book": book_title,
                        "chapter": current_chapter,
                        "verse_number": verse_num,
                        "text_hebrew": verse_text,
                        "text_english": "",
                        "language": "hebrew",
                        "category": "Tanakh",
                        "corpus": "Torat_Emet_Collection",
                        "canonical": True,
                        "source": "Torat Emet",
                        "license": "CC BY-NC-SA 2.5",
                    },
                })
                relationships.append({
                    "type": "PART_OF",
                    "from_id": verse_id,
                    "to_id": current_chapter_id,
                    "properties": {
                        "part_type": "verse_of_chapter",
                        "order_index": verse_num,
                        "confidence": 1.0,
                        "source": "Torat Emet",
                        "extraction_method": "docx_parser",
                    },
                })

    return {
        "book": book_title,
        "nodes": nodes,
        "relationships": relationships,
        "structure": "verse_by_verse",
    }


def parse_free_form(paragraphs: list[dict[str, Any]], book_title: str) -> dict[str, Any]:
    """Parse free-form text (Chassidut, Mussar, etc.) with chunking."""
    nodes: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []

    book_id = book_uuid(book_title)
    nodes.append({
        "id": book_id,
        "label": "Book",
        "properties": {
            "title": book_title,
            "category": "Torah_Literature",
            "corpus": "Torat_Emet_Collection",
            "source": "Torat Emet",
            "license": "CC BY-NC-SA 2.5",
        },
    })

    # Chunk paragraphs into sections (~500 chars each)
    chunks = []
    current_chunk = []
    current_len = 0

    for para in paragraphs:
        text = para["text"]
        if not text:
            continue
        if para["is_heading"] and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0
        current_chunk.append(text)
        current_len += len(text)
        if current_len > 500:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    for i, chunk_text in enumerate(chunks):
        chunk_id = str(uuid.uuid4())
        nodes.append({
            "id": chunk_id,
            "label": "TextChunk",
            "properties": {
                "book": book_title,
                "chunk_number": i + 1,
                "text_hebrew": chunk_text,
                "language": "hebrew",
                "source": "Torat Emet",
                "license": "CC BY-NC-SA 2.5",
            },
        })
        relationships.append({
            "type": "PART_OF",
            "from_id": chunk_id,
            "to_id": book_id,
            "properties": {
                "part_type": "chunk_of_book",
                "order_index": i + 1,
                "confidence": 1.0,
                "source": "Torat Emet",
                "extraction_method": "docx_parser_chunked",
            },
        })

    return {
        "book": book_title,
        "nodes": nodes,
        "relationships": relationships,
        "structure": "free_form_chunked",
    }


def parse_docx(docx_path: Path, book_title: str | None = None) -> dict[str, Any]:
    """Main entry point: parse a .docx file and return structured data."""
    if book_title is None:
        book_title = docx_path.stem

    paragraphs = extract_docx_text(docx_path)
    if not paragraphs:
        logger.warning("docx_empty", path=str(docx_path))
        return {"book": book_title, "nodes": [], "relationships": [], "structure": "empty"}

    structure = detect_structure([p["text"] for p in paragraphs])
    logger.info("docx_structure_detected", path=str(docx_path), structure=structure)

    if structure in ("verse_by_verse", "chapter_based"):
        result = parse_chumash(paragraphs, book_title)
        # If Chumash parser failed to extract verses, fall back to free-form
        if len(result["nodes"]) <= 1:
            logger.info("chumash_parser_empty_fallback", book=book_title)
            return parse_free_form(paragraphs, book_title)
        return result
    else:
        return parse_free_form(paragraphs, book_title)


def save_jsonl(data: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    """Save nodes and relationships as JSONL."""
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^\w֐-׿]+", "_", data["book"]).strip("_")

    nodes_file = output_dir / f"{safe_name}_nodes.jsonl"
    rels_file = output_dir / f"{safe_name}_relationships.jsonl"

    with open(nodes_file, "w", encoding="utf-8") as f:
        for node in data["nodes"]:
            f.write(json.dumps(node, ensure_ascii=False) + "\n")

    with open(rels_file, "w", encoding="utf-8") as f:
        for rel in data["relationships"]:
            f.write(json.dumps(rel, ensure_ascii=False) + "\n")

    logger.info(
        "jsonl_saved",
        book=data["book"],
        nodes=len(data["nodes"]),
        relationships=len(data["relationships"]),
        nodes_file=str(nodes_file),
        relationships_file=str(rels_file),
    )
    return nodes_file, rels_file


def parse_directory(dir_path: Path, output_dir: Path) -> list[dict[str, Any]]:
    """Parse all .docx files in a directory recursively."""
    results = []
    docx_files = list(dir_path.rglob("*.docx"))
    logger.info("directory_scan", path=str(dir_path), files_found=len(docx_files))

    for docx_file in sorted(docx_files):
        try:
            result = parse_docx(docx_file)
            if result["nodes"]:
                save_jsonl(result, output_dir)
                results.append(result)
        except Exception as e:
            logger.error("parse_failed", path=str(docx_file), error=str(e))

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Torah .docx files to Neo4j JSONL")
    parser.add_argument("--input", type=str, help="Single .docx file to parse")
    parser.add_argument("--dir", type=str, help="Directory of .docx files to parse recursively")
    parser.add_argument("--output", type=str, default="data/processed", help="Output directory")
    parser.add_argument("--book-title", type=str, help="Override book title")

    args = parser.parse_args()
    output_dir = Path(args.output)

    if args.input:
        docx_path = Path(args.input)
        if not docx_path.exists():
            print(f"❌ File not found: {docx_path}")
            return
        result = parse_docx(docx_path, args.book_title)
        save_jsonl(result, output_dir)
        print(f"✅ Parsed: {result['book']}")
        print(f"   Nodes: {len(result['nodes'])}, Relationships: {len(result['relationships'])}")
        print(f"   Structure: {result['structure']}")

    elif args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists():
            print(f"❌ Directory not found: {dir_path}")
            return
        results = parse_directory(dir_path, output_dir)
        print(f"✅ Parsed {len(results)} files from {dir_path}")

    else:
        print("❌ Please specify --input or --dir")


if __name__ == "__main__":
    main()
