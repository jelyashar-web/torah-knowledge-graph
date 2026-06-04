# DOCX Import Pipeline — Torah Knowledge Graph

> Import local `.docx` Torah texts (Chassidut, Mussar, Halacha, etc.) into the Neo4j graph.

---

## Overview

The DOCX import pipeline handles **local Torah literature** that is not available via Sefaria API. It scans `.docx` files, extracts Hebrew text with heading detection, normalizes text for search, validates output, and produces Neo4j-ready JSONL.

**Key principle:** No data is loaded into Neo4j until validation passes.

```
.docx library
     │
     ▼
┌─────────────────┐
│ scan_docx_lib   │  →  manifest.json (sha256 + metadata)
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ docx_parser     │  →  *_nodes.jsonl (TextUnit, Book, SourceFile)
│                 │  →  *_relationships.jsonl (PART_OF, NEXT, SOURCE_FILE)
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ validate_textu  │  →  validation_report.json
└─────────────────┘
     │
     ▼ (only if valid)
┌─────────────────┐
│ bulk_load_tanakh│  →  Neo4j (apoc.merge)
└─────────────────┘
```

---

## Scripts

### 1. `scripts/scan_docx_library.py`

Recursively scans a directory tree for `.docx` files and produces a manifest with SHA-256 hashes.

```bash
# Full scan
uv run python scripts/scan_docx_library.py \
    --library-dir /path/to/torah_library \
    --output data/processed/docx_import/manifest.json

# Test mode: first 10 files
uv run python scripts/scan_docx_library.py \
    --library-dir /path/to/torah_library \
    --output data/processed/docx_import/manifest.json \
    --limit 10
```

**Output fields per file:**

| Field | Description |
|-------|-------------|
| `abs_path` | Absolute filesystem path |
| `rel_path` | Path relative to library root |
| `sha256` | SHA-256 hash of file content |
| `size_bytes` | File size |
| `paragraphs` | Paragraph count (from python-docx) |
| `words_estimate` | Approximate word count |
| `chars_estimate` | Approximate character count |

---

### 2. `scripts/docx_parser.py`

Parses `.docx` files into structured **TextUnit** nodes with heading detection.

```bash
# Single file
uv run python scripts/docx_parser.py \
    --input /path/to/file.docx \
    --output data/processed/docx_import/

# Directory (recursive)
uv run python scripts/docx_parser.py \
    --dir /path/to/category/ \
    --output data/processed/docx_import/
```

**Heading Detection:**

The parser detects these Hebrew structural markers:

| Heading | Hebrew Pattern | Example |
|---------|---------------|---------|
| Chapter | `פרק` | `פרק א` |
| Section | `סימן` | `סימן יב` |
| Clause | `סעיף` | `סעיף ג` |
| Law | `הלכה` | `הלכה ד` |
| Mishna | `משנה` | `משנה ה` |
| Daf | `דף` | `דף ב` |
| Amud | `עמוד` | `עמוד א` |
| Gate | `שער` | `שער ג` |
| Drush | `דרוש` | `דרוש א` |
| Letter | `אות` | `אות ה` |

**Node Schema:**

```json
// TextUnit
{
  "id": "uuid",
  "label": "TextUnit",
  "properties": {
    "book": "Likutei Moharan",
    "unit_number": 1,
    "text_hebrew": "בס״ד אמרו חכמים...",
    "text_hebrew_normalized": "בסד אמרו חכמים...",
    "is_heading": false,
    "heading_type": null,
    "hierarchy_level": null,
    "paragraph_index": 0,
    "style": "Normal",
    "language": "hebrew",
    "source": "Torat Emet",
    "license": "CC BY-NC-SA 2.5"
  }
}
```

**Relationship Types:**

| Type | From | To | Meaning |
|------|------|-----|---------|
| `PART_OF` | TextUnit | Book | Unit belongs to book |
| `NEXT` | TextUnit | TextUnit | Sequential reading order |
| `SOURCE_FILE` | Book | SourceFile | Origin document |

---

### 3. `scripts/import_docx_collection.py`

Orchestrates the full pipeline: scan → parse → validate → (optional) Neo4j load.

```bash
# Full pipeline with validation
uv run python scripts/import_docx_collection.py \
    --library-dir /path/to/torah_library \
    --output-dir data/processed/docx_import/ \
    --validate

# Test mode: 10 files
uv run python scripts/import_docx_collection.py \
    --library-dir /path/to/torah_library \
    --output-dir data/processed/docx_import/ \
    --limit 10 \
    --validate

# Skip scan (use existing manifest)
uv run python scripts/import_docx_collection.py \
    --manifest data/processed/docx_import/manifest.json \
    --output-dir data/processed/docx_import/ \
    --validate \
    --load-neo4j
```

---

### 4. `scripts/validate_textunits.py`

Validates parsed JSONL before any Neo4j write.

```bash
uv run python scripts/validate_textunits.py \
    --data-dir data/processed/docx_import/ \
    --output data/processed/docx_import/validation_report.json
```

**Validation checks:**

| # | Check | Severity |
|---|-------|----------|
| 1 | No empty `text_hebrew` | Error |
| 2 | `text_hebrew_normalized` present | Warning |
| 3 | Hebrew characters exist in text | Error |
| 4 | No duplicate node IDs across files | Error |
| 5 | All relationship `from_id` exist in nodes | Error |
| 6 | All relationship `to_id` exist in nodes | Error |
| 7 | Valid UTF-8 encoding | Error |

---

## Node Labels

| Label | Count | Description |
|-------|-------|-------------|
| `Book` | 1 per file | The work as a whole |
| `TextUnit` | N per file | Individual paragraphs/sections |
| `SourceFile` | 1 per file | Original `.docx` metadata |

---

## Data Flow

```
Torat Emet .docx files
        │
        ▼
┌─────────────────────────────────────┐
│  scan_docx_library.py               │
│  → manifest.json (sha256, metadata)  │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  docx_parser.py                     │
│  → *_nodes.jsonl                     │
│  → *_relationships.jsonl             │
│  → text_hebrew_normalized            │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  validate_textunits.py              │
│  → validation_report.json          │
│  → PASS / FAIL                       │
└─────────────────────────────────────┘
        │ (only if PASS)
        ▼
┌─────────────────────────────────────┐
│  bulk_load_tanakh.py                │
│  → Neo4j (apoc.merge.node)           │
│  → Neo4j (apoc.merge.relationship)   │
└─────────────────────────────────────┘
```

---

## Testing

### Dry Run (no Neo4j write)

```bash
# 1. Scan
uv run python scripts/scan_docx_library.py \
    --library-dir ~/TorahLibrary \
    --output /tmp/test_manifest.json \
    --limit 10

# 2. Parse
uv run python scripts/docx_parser.py \
    --dir ~/TorahLibrary \
    --output /tmp/docx_test/

# 3. Validate
uv run python scripts/validate_textunits.py \
    --data-dir /tmp/docx_test/ \
    --output /tmp/validation_report.json
```

### Expected Output (10 files)

```text
✅ Parsed 10 files → 20 JSONL files
   Units: ~500 TextUnit nodes
   Books: 10 Book nodes
   Relationships: ~500 PART_OF + ~450 NEXT

✅ VALIDATION PASSED
   Errors: 0
   Warnings: 0
```

---

## Integration with Neo4j

After validation passes, load into Neo4j:

```bash
uv run python scripts/bulk_load_tanakh.py \
    --data-dir data/processed/docx_import/ \
    --batch-size 500
```

This reuses the same bulk loader as Tanakh JSONL files.

---

## Notes

- All Hebrew text is **UTF-8**. Cantillation marks are preserved in `text_hebrew` but removed in `text_hebrew_normalized`.
- The `NEXT` relationship preserves **sequential reading order** within a document.
- `SOURCE_FILE` relationships enable tracing any node back to its original `.docx` file.
- SHA-256 hashes enable detecting **duplicate files** across the library.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `python-docx not found` | Run `uv sync` or `pip install python-docx` |
| Validation fails on Hebrew | Check file encoding — must be UTF-8 |
| Empty nodes | The `.docx` may be scanned image-only; use OCR first |
| Duplicate IDs | Run parser again; IDs are regenerated each time |

---

> *"Every paragraph is a TextUnit. Every TextUnit is Connected."*
