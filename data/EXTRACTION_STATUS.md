# Torah Knowledge Graph — Extraction Status
## Data Ingestion Tracker

**Last Updated:** 2026-06-04
**Source:** Sefaria.org API
**Rate Limit:** 1.1 seconds between requests

---

## Extraction Pipeline

### Stage 1: Raw Extraction
Python script `scripts/sefaria_extractor.py` fetches texts from Sefaria API chapter by chapter.
- Hebrew text (`he` field)
- English translation (`text` field)
- Metadata (title, category, schema, versions)
- Saved as JSON: `data/raw/{Book}.json`

### Stage 2: Transformation
Python script `scripts/transform_for_neo4j.py` converts raw JSON to Neo4j-ready JSONL.
- Verse nodes with Hebrew text, English text, references
- Chapter nodes
- Book nodes
- PART_OF relationships (Verse → Chapter → Book)
- HTML cleaned, entities decoded
- Saved as JSONL: `data/processed/{Book}_nodes.jsonl` and `{Book}_relationships.jsonl`

### Stage 3: Neo4j Bulk Import (Pending)
Use `neo4j-admin database import` or Cypher `LOAD CSV` / `apoc.load.json` to ingest JSONL.

---

## Extracted Books

### ✅ Torah (Complete — 5/5 books)

| Book | Chapters | Raw Size | Nodes | Relationships | Status |
|------|----------|----------|-------|-----------------|--------|
| Genesis | 50 | 6.1 MB | 1,584 | 1,583 | ✅ Extracted + Transformed |
| Exodus | 40 | 4.7 MB | 1,251 | 1,250 | ✅ Extracted + Transformed |
| Leviticus | 27 | 3.1 MB | — | — | ✅ Extracted + Transformed |
| Numbers | 36 | — | 1,325 | 1,324 | ✅ Extracted + Transformed |
| Deuteronomy | 34 | — | 991 | 990 | ✅ Extracted + Transformed |
| **Total Torah** | **187** | **~14 MB** | **~5,150** | **~5,147** | **✅ Complete** |

### ⏳ Nevi'im (Prophets) — Not Started

| Book | Chapters | Status |
|------|----------|--------|
| Joshua | 24 | ⏳ Pending |
| Judges | 21 | ⏳ Pending |
| I Samuel | 31 | ⏳ Pending |
| II Samuel | 24 | ⏳ Pending |
| I Kings | 22 | ⏳ Pending |
| II Kings | 25 | ⏳ Pending |
| Isaiah | 66 | ⏳ Pending |
| Jeremiah | 52 | ⏳ Pending |
| Ezekiel | 48 | ⏳ Pending |
| Twelve Minor Prophets | 67 | ⏳ Pending |

### ⏳ Ketuvim (Writings) — Not Started

| Book | Chapters | Status |
|------|----------|--------|
| Psalms | 150 | ⏳ Pending |
| Proverbs | 31 | ⏳ Pending |
| Job | 42 | ⏳ Pending |
| Song of Songs | 8 | ⏳ Pending |
| Ruth | 4 | ⏳ Pending |
| Lamentations | 5 | ⏳ Pending |
| Ecclesiastes | 12 | ⏳ Pending |
| Esther | 10 | ⏳ Pending |
| Daniel | 12 | ⏳ Pending |
| Ezra | 10 | ⏳ Pending |
| Nehemiah | 13 | ⏳ Pending |
| I Chronicles | 29 | ⏳ Pending |
| II Chronicles | 36 | ⏳ Pending |

### ⏳ Mishnah — Not Started

| Tractate | Chapters | Status |
|----------|----------|--------|
| Berakhot | 9 | ⏳ Pending |
| Shabbat | 24 | ⏳ Pending |
| Eruvin | 10 | ⏳ Pending |
| Pesahim | 10 | ⏳ Pending |
| Yoma | 8 | ⏳ Pending |
| Sukkah | 5 | ⏳ Pending |
| ... (52 tractates total) | ... | ⏳ Pending |

### ⏳ Talmud Bavli — Not Started

| Tractate | Pages | Status |
|----------|-------|--------|
| Berakhot | 64 | ⏳ Pending |
| Shabbat | 157 | ⏳ Pending |
| Eruvin | 105 | ⏳ Pending |
| ... (36 tractates total) | ~2,700 | ⏳ Pending |

### ⏳ Kabbalah — Not Started

| Book | Sections | Status |
|------|----------|--------|
| Zohar | ~1,800 | ⏳ Pending |
| Tikkunei Zohar | 70 | ⏳ Pending |
| Etz Chaim | 50 | ⏳ Pending |
| Tanya | 53 | ⏳ Pending |
| Likutei Moharan | ~300 | ⏳ Pending |

### ⏳ Halachic Codes — Not Started

| Book | Sections | Status |
|------|----------|--------|
| Shulchan Aruch, Orach Chayim | 697 | ⏳ Pending |
| Shulchan Aruch, Yoreh De'ah | 403 | ⏳ Pending |
| Mishneh Torah | ~1,000 | ⏳ Pending |

---

## Batch Extraction Commands

### Extract a single book
```bash
python3 scripts/sefaria_extractor.py --book "Genesis" --output data/raw/
python3 scripts/transform_for_neo4j.py --input data/raw/Genesis.json --output data/processed/
```

### Extract a phase (batch)
```bash
python3 scripts/batch_extract.py --phase-file data/manifests/phase2_neviim.txt --output data/
```

### Extract all priority-1 books
```bash
python3 scripts/batch_extract.py --manifest data/manifests/torah_corpus_manifest.json --phase 1
```

---

## Data Format

### Raw JSON Structure
```json
{
  "title": "Genesis",
  "hebrew_title": "בראשית",
  "category": ["Tanakh", "Torah"],
  "schema": { /* Sefaria schema */ },
  "refs": {
    "Genesis 1": {
      "hebrew": { "text": ["verse1", "verse2", ...], "he": ["בראשית...", ...] },
      "english": { "text": ["In the beginning...", ...], "he": [...] }
    },
    "Genesis 2": { ... }
  }
}
```

### Neo4j JSONL Structure

**Nodes (`{book}_nodes.jsonl`):**
```json
{"id": "uuid", "label": "Book", "properties": {"title": "Genesis", "hebrew_title": "בראשית", ...}}
{"id": "uuid", "label": "Chapter", "properties": {"ref": "Genesis 1", "number": 1, ...}}
{"id": "uuid", "label": "Verse", "properties": {"ref": "Genesis 1:1", "text_hebrew": "בְּרֵאשִׁית...", "text_english": "In the beginning...", ...}}
```

**Relationships (`{book}_relationships.jsonl`):**
```json
{"type": "PART_OF", "from_id": "verse-uuid", "to_id": "chapter-uuid", "properties": {"part_type": "verse_of_chapter", "confidence": 1.0, "source": "canonical"}}
```

---

## Known Issues

1. **Sefaria API returns HTML in text** — Transformer cleans HTML tags and decodes entities.
2. **Some books have complex schema** — Nested nodes (e.g., Parasha structure in Torah) may need manual handling.
3. **Talmud daf structure** — References use "DafAmud" format (e.g., "Berakhot 2a") which requires different parsing.
4. **Rate limiting** — 1.1s between requests. Full corpus extraction (~250 books) estimated at ~40 hours.
5. **English translations vary** — Different editions (Koren, JPS, etc.). Sefaria returns default translation.

---

## Next Steps

1. ✅ Torah extraction complete
2. ⏳ Extract Nevi'im (21 books)
3. ⏳ Extract Ketuvim (13 books)
4. ⏳ Extract Mishnah (52 tractates)
5. ⏳ Extract Talmud Bavli core (11 tractates for Phase 1)
6. ⏳ Extract Kabbalah core (Zohar, Tanya)
7. ⏳ Extract Halachic codes (Shulchan Aruch, Rambam)
8. ⏳ Bulk import into Neo4j
9. ⏳ Create vector embeddings for Qdrant
