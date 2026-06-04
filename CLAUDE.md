# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important: Project State

This is the **Torah Knowledge Graph** — a graph-native knowledge platform for Torah literature. The project is currently in the **design + data extraction phase**. Most directories (`backend/`, `frontend/`, `shared/`, `etl/`, `ai-extraction/`) contain design documents only; the only runnable code lives in `scripts/`.

## Working with Extraction Scripts

The `scripts/` directory contains the current working toolchain:

- **`sefaria_extractor.py`** — Fetches texts from Sefaria API (1 req/sec rate limit enforced via `time.sleep(1.1)`)
- **`transform_for_neo4j.py`** — Converts raw Sefaria JSON into Neo4j-ready JSONL nodes + relationships
- **`batch_extract.py`** — Orchestrates extract → transform for multiple books

All scripts run with `uv run python scripts/<script>.py`. There is no root `pyproject.toml` yet; `uv` is used because the project conventions specify it as the Python package manager.

### Common Commands

```bash
# Extract a single book
uv run python scripts/sefaria_extractor.py --book Genesis --output data/raw/

# Extract from manifest (phased extraction plan)
uv run python scripts/sefaria_extractor.py --manifest data/manifests/torah_corpus_manifest.json --phase 1

# Transform raw JSON to Neo4j JSONL
uv run python scripts/transform_for_neo4j.py --input data/raw/Genesis.json --output data/processed/

# Batch extract + transform multiple books
uv run python scripts/batch_extract.py --books Genesis Exodus Leviticus --output data/

# Batch via phase file
uv run python scripts/batch_extract.py --phase-file data/manifests/phase1_torah.txt --output data/
```

**Rate limiting:** Sefaria requires **1 request per second**. The extractor enforces this with `RATE_LIMIT_SECONDS = 1.1` between each API call. Do not remove or reduce this delay.

## Data Pipeline Architecture

The current data flow is a two-stage pipeline:

```
Sefaria API  →  scripts/sefaria_extractor.py  →  data/raw/{book}.json
                                                    ↓
scripts/transform_for_neo4j.py  →  data/processed/{book}_nodes.jsonl
                                     data/processed/{book}_relationships.jsonl
```

### Node Types Produced

- **`Book`** — One per extracted book (e.g., Genesis)
- **`Chapter`** — One per chapter, linked to Book via `PART_OF`
- **`Verse`** — One per verse, linked to Chapter via `PART_OF`

### Relationship Types

- **`PART_OF`** — Chapter→Book (`part_type: chapter_of_book`) and Verse→Chapter (`part_type: verse_of_chapter`)

All relationships carry provenance metadata: `confidence: 1.0`, `source: canonical`, `extraction_method: imported`.

## Project Structure (Design Phase)

The full architecture is documented in `architecture/SYSTEM_ARCHITECTURE.md` and `docs/FOLDER_STRUCTURE.md`. Key directories:

| Directory | Status | Contents |
|-----------|--------|----------|
| `scripts/` | **Active** | Working Python extraction + transform code |
| `data/` | **Active** | Raw JSON (`data/raw/`) and processed JSONL (`data/processed/`) |
| `architecture/` | Design | System architecture, Neo4j schema, API spec |
| `docs/` | Design | Implementation roadmap, folder structure plan |
| `etl/` | Design | ETL pipeline design document only |
| `ontology/` | Research | V1/V2/V3 ontology iterations + deliverables |
| `backend/` | **Empty** | FastAPI app planned; only `UI_DESIGN.md` exists |
| `frontend/` | **Empty** | Next.js app planned; only `UI_DESIGN.md` exists |
| `shared/` | **Missing** | Shared types planned but not created |
| `databases/` | Design | PostgreSQL + Qdrant schema docs; no migration files yet |
| `infrastructure/` | Design + Compose | `docker-compose.yml` is the primary runnable infra file |
| `ai-extraction/` | Design | AI extraction design doc only |

## Docker Compose

`infrastructure/docker-compose.yml` defines the full stack (Neo4j, PostgreSQL, Qdrant, Redis, FastAPI backend, Celery workers, Next.js frontend). Currently the `backend`, `worker`, `beat`, and `frontend` services **will fail to build** because their build contexts (`./backend`, `./frontend`) are empty.

To start only the databases:
```bash
docker-compose up -d neo4j postgres qdrant redis
```

Neo4j Browser: `http://localhost:7474` (user: `neo4j`, password: `torah-graph-secure`)

## Key Design Conventions

### Code Style (from `CONTRIBUTING.md`)
- **Python**: Ruff (line-length 100), pyright strict mode, `uv` for dependency management
- **TypeScript**: ESLint + Prettier, strict `tsconfig.json`
- **Comments/docs**: Hebrew permitted for internal notes; English for external-facing docs and code comments

### Commit Messages
Use conventional commits with Torah-specific scopes:
- `feat(api)`, `fix(graph)`, `content(ontology)`, `refactor(etl)`, `test(ai)`, `docs`
- Example: `content(ontology): add Rambam's 13 Principles as concept nodes`

### Hebrew Text Handling
- Always UTF-8
- Preserve original Hebrew spelling (do not normalize)
- Cantillation marks preserved when available
- RTL is first-class

### Critical Rules (from `README.md` and `CONTRIBUTING.md`)
- **Never invent Torah sources.** Every relationship requires a real citation.
- **Never fabricate citations.** Exact references only (book, chapter, verse, page, daf).
- **Always track provenance.** Model, prompt, temperature, validator.
- **Distinguish:** Explicit source | Derived relationship | AI-inferred relationship.
- **Soul Root Graph is RESTRICTED.** No AI extraction. Only manual curation from Zohar, Etz Chaim, Shaar HaGilgulim, or writings of Arizal / Rashash / Vilna Gaon.

## Technology Stack (Planned)

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, React Flow, D3.js |
| Backend | FastAPI, Python 3.12+, Pydantic v2, SQLAlchemy 2 |
| Graph DB | Neo4j Community 5.x (APOC + GDS plugins) |
| Relational DB | PostgreSQL 16 |
| Vector DB | Qdrant 1.x |
| Queue | Redis 7 + Celery 5 |
| Infrastructure | Docker Compose |

## Data Manifest

`data/manifests/torah_corpus_manifest.json` is the canonical catalog of all ~250 books to extract from Sefaria, organized by category (Tanakh, Mishnah, Tosefta, Talmud Bavli/Yerushalmi, Midrash Rabbah, Tanchuma, Yalkut Shimoni, Zohar, Tikkunei Zohar, Lurianic Kabbalah, Rashash, Chassidut, Shulchan Aruch, Rambam Mishneh Torah, Commentaries, Musar). Each category has priority levels (1 = highest). Phase files in `data/manifests/phase*.txt` list books for incremental extraction.

## Neo4j Bulk Import

Processed JSONL files follow Neo4j bulk-import format:
- `_nodes.jsonl`: `{id, label, properties: {...}}`
- `_relationships.jsonl`: `{type, from_id, to_id, properties: {...}}`

These can be loaded via `neo4j-admin database import` or Cypher `UNWIND` batches once Neo4j is running.
