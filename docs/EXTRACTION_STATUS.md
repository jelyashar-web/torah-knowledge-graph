# Extraction Status — Torah Knowledge Graph

> **Source:** Sefaria.org API  
> **Rate Limit:** 1 request per second  
> **Pipeline:** `sefaria_extractor.py` → `transform_for_neo4j.py`  
> **Last Updated:** 2026-06-04

---

## Extracted Books

| Book | Category | Chapters | Raw Size | Nodes JSONL | Relationships JSONL | Status |
|------|----------|----------|----------|-------------|---------------------|--------|
| Genesis | Torah | 50 | 6.1M | Genesis_nodes.jsonl | Genesis_relationships.jsonl | ✅ |
| Exodus | Torah | 40 | 4.7M | Exodus_nodes.jsonl | Exodus_relationships.jsonl | ✅ |
| Leviticus | Torah | 27 | 3.1M | Leviticus_nodes.jsonl | Leviticus_relationships.jsonl | ✅ |
| Numbers | Torah | 36 | 4.2M | Numbers_nodes.jsonl | Numbers_relationships.jsonl | ✅ |
| Deuteronomy | Torah | 34 | 3.9M | Deuteronomy_nodes.jsonl | Deuteronomy_relationships.jsonl | ✅ |
| Psalms | Ketuvim | 150 | 10.0M | Psalms_nodes.jsonl | Psalms_relationships.jsonl | ✅ |
| Proverbs | Ketuvim | 31 | 2.1M | Proverbs_nodes.jsonl | Proverbs_relationships.jsonl | ✅ |
| Job | Ketuvim | 42 | 2.8M | Job_nodes.jsonl | Job_relationships.jsonl | ✅ |

**Total extracted:** 8 books | **Total raw data:** ~37 MB

---

## Pending Extraction — Tanakh

### Phase 2: Nevi'im (Prophets) — 21 books

| Book | Chapters (est.) | Priority |
|------|-----------------|----------|
| Joshua | 24 | High |
| Judges | 21 | High |
| I Samuel | 31 | High |
| II Samuel | 24 | High |
| I Kings | 22 | High |
| II Kings | 25 | High |
| Isaiah | 66 | High |
| Jeremiah | 52 | High |
| Ezekiel | 48 | High |
| Hosea | 14 | Medium |
| Joel | 3 | Medium |
| Amos | 9 | Medium |
| Obadiah | 1 | Medium |
| Jonah | 4 | Medium |
| Micah | 7 | Medium |
| Nahum | 3 | Medium |
| Habakkuk | 3 | Medium |
| Zephaniah | 3 | Medium |
| Haggai | 2 | Medium |
| Zechariah | 14 | Medium |
| Malachi | 3 | Medium |

### Phase 3: Remaining Ketuvim — 10 books

| Book | Chapters (est.) | Priority |
|------|-----------------|----------|
| Song of Songs | 8 | High |
| Ruth | 4 | High |
| Lamentations | 5 | High |
| Ecclesiastes | 12 | High |
| Esther | 10 | High |
| Daniel | 12 | High |
| Ezra | 10 | High |
| Nehemiah | 13 | High |
| I Chronicles | 29 | High |
| II Chronicles | 36 | High |

---

## Extraction Pipeline

### Stage 1: Raw Extraction

```bash
# Extract a single book
uv run python scripts/sefaria_extractor.py --book Genesis --output data/raw/

# Extract from a phase file (batch)
uv run python scripts/batch_extract.py --phase-file data/manifests/phase1_torah.txt --output data/
```

**What happens:**
1. Fetch book index from Sefaria API
2. For each chapter: fetch Hebrew text + English text
3. Rate limit: `time.sleep(1.1)` between each request
4. Save structured JSON to `data/raw/{book}.json`

### Stage 2: Transform to Neo4j JSONL

```bash
# Transform a single book
uv run python scripts/transform_for_neo4j.py --input data/raw/Genesis.json --output data/processed/
```

**What happens:**
1. Parse raw JSON into typed nodes: `Book`, `Chapter`, `Verse`
2. Generate `PART_OF` relationships with provenance metadata
3. Output:
   - `data/processed/{book}_nodes.jsonl`
   - `data/processed/{book}_relationships.jsonl`

### Node Schema

```json
// Book node
{"id": "uuid", "label": "Book", "properties": {"title": "Genesis", "hebrewTitle": "בראשית", "category": ["Tanakh", "Torah"]}}

// Chapter node
{"id": "uuid", "label": "Chapter", "properties": {"number": 1, "book": "Genesis"}}

// Verse node
{"id": "uuid", "label": "Verse", "properties": {"number": 1, "chapter": 1, "book": "Genesis", "hebrewText": "...", "englishText": "..."}}
```

### Relationship Schema

```json
{"type": "PART_OF", "from_id": "chapter-uuid", "to_id": "book-uuid", "properties": {"part_type": "chapter_of_book", "confidence": 1.0, "source": "canonical", "extraction_method": "imported"}}
{"type": "PART_OF", "from_id": "verse-uuid", "to_id": "chapter-uuid", "properties": {"part_type": "verse_of_chapter", "confidence": 1.0, "source": "canonical", "extraction_method": "imported"}}
```

---

## Notes

- All Hebrew text is UTF-8, cantillation marks preserved when available.
- Sefaria API rate limit is strictly enforced (1.1s between requests).
- Failed chapters are logged but do not stop the batch.
- For bulk import into Neo4j, see `scripts/load_jsonl_to_neo4j.py`.
