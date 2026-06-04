# Torah Knowledge Graph

> **A living knowledge graph of all Torah literature — Tanakh, Mishnah, Tosefta, Bavli, Yerushalmi, Midrash Rabbah, Tanchuma, Yalkut Shimoni, Zohar, Tikkunei Zohar, Etz Chaim, Pri Etz Chaim, Shaar HaKavanot, Rashash, Tanya, Likutei Moharan, Shulchan Aruch, Rambam, and all major commentators.**

---

## Overview

The Torah Knowledge Graph (TKG) is a **graph-native knowledge platform** built around a single principle:

> **Everything is a Node. Everything is Connected.**

Every verse, chapter, book, person, tzaddik, mitzvah, concept, sefirah, divine name, prayer, promise, segulah, tikkun, place, historical event, and halachic topic is a node in a Neo4j graph. Every connection is a typed, directed relationship with full provenance, confidence scoring, and source tracking.

This is **not** a RAG system. **Not** a search engine. **Not** a chatbot. It is a living graph database of Torah knowledge with unique layers for promises, segulot, tikkunim, middot, divine names, sefirot, and soul roots.

---

## Extraction Progress

| Phase | Books | Extracted | Status |
|-------|-------|-----------|--------|
| **1 — Torah** | Genesis, Exodus, Leviticus, Numbers, Deuteronomy | 5/5 | ✅ Complete |
| **2 — Nevi'im** | Joshua, Judges, I Samuel, II Samuel, I Kings, II Kings, Isaiah, Jeremiah, Ezekiel, Hosea, Joel, Amos, Obadiah, Jonah, Micah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah, Malachi | 0/21 | ⏳ In Progress |
| **3 — Ketuvim** | Psalms, Proverbs, Job, Song of Songs, Ruth, Lamentations, Ecclesiastes, Esther, Daniel, Ezra, Nehemiah, I Chronicles, II Chronicles | 3/13 | 🔄 Partial |
| **4 — Mishnah** | 63 tractates | 0/63 | 📋 Planned |
| **5 — Talmud Bavli** | 37 tractates | 0/37 | 📋 Planned |
| **6 — Kabbalah** | Zohar, Tikkunei Zohar, etc. | 0/? | 📋 Planned |
| **7 — Halacha** | Shulchan Aruch, Rambam, etc. | 0/? | 📋 Planned |

> **Last updated:** 2026-06-04  
> **Source:** Sefaria.org API (1 req/sec rate limit)  
> **Format:** Hebrew + English, verse-level JSON → Neo4j JSONL

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│           Next.js 15 + TypeScript + Tailwind CSS             │
│           React Flow + D3.js (interactive graph views)       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND LAYER                            │
│              FastAPI (Python 3.12+) + async                  │
│              Celery + Redis (background jobs)                │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
    ┌────┴────┐        ┌──────┴──────┐      ┌─────┴─────┐
    │  Neo4j  │        │ PostgreSQL  │      │  Qdrant   │
    │  Graph  │        │ Operational │      │  Vector   │
    └─────────┘        └─────────────┘      └───────────┘
```

### Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend** | Next.js 15, TypeScript, Tailwind, React Flow, D3.js | 15.x |
| **Backend** | FastAPI, Python, Pydantic v2, SQLAlchemy 2 | 3.12+, 0.115+ |
| **Graph DB** | Neo4j Community (APOC + GDS plugins) | 5.x |
| **Relational DB** | PostgreSQL 16 | 16.x |
| **Vector DB** | Qdrant | 1.x |
| **Queue** | Redis + Celery | 7.x, 5.x |
| **Infrastructure** | Docker + Docker Compose | 25.x |

---

## Core Design Principles

1. **Everything is a Node** — All Torah entities are typed nodes in Neo4j with full property schemas.
2. **Everything is Connected** — All relationships are directed, typed, and carry provenance (source, confidence, extraction method).
3. **Multi-Dimensional** — The same concept exists in different domains with different meanings, linked by cross-dimensional relationships.
4. **Dispute Preservation** — When authorities disagree, ALL opinions are first-class objects. No opinion is marked as "correct."
5. **Source Binding** — Every assertion must be bound to a specific textual source. Unsourced assertions are invalid.
6. **Hebrew-First** — Every entity has a Hebrew name. Hebrew text preserves cantillation. RTL is first-class.

---

## Graph Layers

The graph is not a monolithic dump. It is organized into **specialized views** that almost nobody has built:

| Layer | Description | Nodes |
|-------|-------------|-------|
| **Promises Graph** | Divine promises, conditions, beneficiaries | ~1,200 |
| **Segulot Graph** | Remedies, purposes, requirements, sources | ~800 |
| **Tikkun Graph** | Sins, damages, repair methods | ~600 |
| **Middot Graph** | Character traits, effects, sources | ~400 |
| **Divine Names Graph** | Names of God, gematria, sefirot associations | ~72 |
| **Sefirot Graph** | Ten emanations, partzufim, correspondences | ~10 |
| **Soul Root Graph** | Authoritative sources only (Zohar, Arizal, Rashash, Vilna Gaon) | ~12 |

> **Critical Rule:** Soul Root Graph is RESTRICTED. No AI extraction. Only manual curation from Zohar, Etz Chaim, Shaar HaGilgulim, or writings of Arizal / Rashash / Vilna Gaon.

---

## Node Types (16)

`Verse`, `Chapter`, `Book`, `Person`, `Tzaddik`, `Mitzvah`, `Concept`, `Sefirah`, `DivineName`, `Prayer`, `Promise`, `Segulah`, `Tikkun`, `Place`, `HistoricalEvent`, `HalachicTopic`

## Relationship Types (28+)

`COMMENTARY_ON`, `QUOTES`, `MENTIONS`, `RELATED_TO`, `DERIVED_FROM`, `CAUSES`, `REPAIRS`, `PROMISES`, `SEGULAH_FOR`, `TIKKUN_FOR`, `DISPUTES`, `AGREES_WITH`, `PART_OF`, `SOURCE_FOR`, `EXPANDS`, `CONTRADICTS`, `SUBSUMES`, `INSTANCE_OF`, `COMPOSES`, `EMANATES_FROM`, `CORRESPONDS_TO`, `BALANCES`, `TEACHER_OF`, `STUDENT_OF`, `DISCIPLE_OF`, `RESPONDS_TO`, `UNITY_ACROSS_DOMAINS`

---

## Project Structure

```
torah-knowledge-graph/
├── architecture/          # System architecture, Neo4j schema, API spec
├── backend/               # FastAPI app, models, services, workers
├── databases/             # PostgreSQL schema, Qdrant schema, Neo4j schema
├── docs/                  # Documentation, folder structure, roadmap
├── etl/                   # ETL pipelines for Sefaria, exports, open datasets
├── ai-extraction/         # AI extraction service, prompts, validators
├── frontend/              # Next.js app, components, graph views
├── infrastructure/          # Docker Compose, Docker architecture
├── ontology/              # Torah Ontology research (V1, V2, V3)
├── shared/                # Shared types, constants, OpenAPI spec
└── README.md
```

---

## Quick Start

### Current Working Pipeline (Data Extraction)

```bash
# Extract a single book from Sefaria
uv run python scripts/sefaria_extractor.py --book Genesis --output data/raw/

# Extract multiple books via batch
uv run python scripts/batch_extract.py --books Genesis Exodus Leviticus --output data/

# Extract from a phase manifest
uv run python scripts/batch_extract.py --phase-file data/manifests/phase1_torah.txt --output data/

# Transform raw JSON to Neo4j JSONL
uv run python scripts/transform_for_neo4j.py --input data/raw/Genesis.json --output data/processed/
```

### Infrastructure (Databases Only)

```bash
# Start databases (Neo4j, PostgreSQL, Qdrant, Redis)
docker-compose up -d neo4j postgres qdrant redis

# Neo4j Browser: http://localhost:7474
#   User: neo4j | Password: torah-graph-secure
```

> **Note:** Backend (`backend/`), frontend (`frontend/`), and worker services in `docker-compose.yml` currently have **empty build contexts** and will fail to start. Only database services are runnable today.

---

## Documentation

| Document | Description |
|----------|-------------|
| `architecture/SYSTEM_ARCHITECTURE.md` | Full system architecture with service diagram |
| `architecture/NEO4J_SCHEMA.md` | 16 node labels, 18+ relationship types, constraints, indexes, Cypher examples |
| `architecture/API_SPECIFICATION.md` | 50+ REST endpoints, WebSocket protocol, OpenAPI-style schemas |
| `databases/POSTGRESQL_SCHEMA.md` | 8 tables: users, sources, texts, jobs, audit, AI metadata, confidence, API logs |
| `databases/QDRANT_SCHEMA.md` | 2 vector collections (torah_texts, torah_entities), 768-dim Cosine, HNSW |
| `docs/EXTRACTION_STATUS.md` | Current extraction progress, pipeline docs, node/relationship schemas |
| `docs/IMPLEMENTATION_ROADMAP.md` | 7 phases over 20 weeks with milestone gates |
| `docs/FOLDER_STRUCTURE.md` | Complete frontend/backend/ETL/AI/infrastructure folder hierarchy |
| `etl/ETL_DESIGN.md` | Sefaria API ingestion, bulk export loading, open dataset adapters |
| `ai-extraction/AI_EXTRACTION_DESIGN.md` | Entity/relationship extraction, confidence scoring, human validation queue |
| `frontend/UI_DESIGN.md` | 5 graph views, node detail panel, search, layer selector, accessibility |
| `infrastructure/DOCKER_ARCHITECTURE.md` | 8 services with health checks, dependencies, production guidance |
| `ontology/deliverables/01_ONTOLOGY_BLUEPRINT.md` | Formal ontology: entities, rules, validation |
| `ontology/deliverables/02_RELATIONSHIP_TAXONOMY.md` | 28 relationship types with evidence requirements |
| `ontology/deliverables/03_500_TORAH_CONCEPTS.md` | 500 real concepts stress-tested across 5 domains |
| `ontology/models/DISPUTE_MODEL.md` | 7 dispute types, Dispute Engine architecture |
| `ontology/models/EVIDENCE_MODEL.md` | 7 evidence levels, validation rules, AI extraction pipeline |
| `ontology/models/LEARNING_MODEL.md` | 8-stage learning pipeline for new books |
| `ontology/models/VALIDATION_MODEL.md` | 5 validation levels, diversity requirements |
| `ontology/v1/ONTOLOGY_V1.md` | Baseline: 70% clean, 30% flagged |
| `ontology/v2/ONTOLOGY_V2.md` | Dimensional layers: 90% clean |
| `ontology/v3/ONTOLOGY_V3.md` | Meta-ontological layer: 100% clean |

---

## Ingestion Flow (Current Working Pipeline)

**Stage 1 — Extract:**
```
uv run python scripts/batch_extract.py --phase-file data/manifests/phase1_torah.txt --output data/
    │
    ├─ sefaria_extractor.py → fetch index → total_refs=N
    │   for chapter in 1..N:
    │       sleep 1.1s → GET /texts/Genesis%20{chapter}?lang=he
    │       sleep 1.1s → GET /texts/Genesis%20{chapter}?lang=en
    │   save → data/raw/Genesis.json
    │
    └─ transform_for_neo4j.py → parse verses → typed nodes
        save → data/processed/Genesis_nodes.jsonl
        save → data/processed/Genesis_relationships.jsonl
```

**Stage 2 — Load into Neo4j (manual):**
```bash
# Use Cypher UNWIND or neo4j-admin import
python scripts/load_jsonl_to_neo4j.py --nodes data/processed/Genesis_nodes.jsonl --relationships data/processed/Genesis_relationships.jsonl
```

> **Future:** The full FastAPI → PostgreSQL → Celery pipeline is planned for Phase 3 (see `docs/IMPLEMENTATION_ROADMAP.md`). Today, extraction runs directly via Python scripts.

## Search Flow

```
GET /api/v1/search/fulltext?q=בראשית
    → Neo4j Full-Text Index (verseHebrewText)
    → RETURN verse, score

GET /api/v1/search/semantic?q=creation+of+the+world
    → OpenAI embedding(query)
    → Qdrant cosine similarity search
    → MATCH (v:Verse {id: payload.neo4j_node_id}) RETURN v

GET /api/v1/search/hybrid?q=light+on+first+day
    → Fulltext results + rank
    → Semantic results + rank
    → RRF (Reciprocal Rank Fusion): score = Σ 1/(k + rank)
    → Merge, deduplicate, rerank, return top-k
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `NEO4J_PASSWORD` | Yes | `torah-graph-secure` | Neo4j auth |
| `POSTGRES_PASSWORD` | Yes | `tkg-postgres-secure` | PostgreSQL auth |
| `JWT_SECRET` | Yes | `change-me...` | JWT signing |
| `OPENAI_API_KEY` | No | — | Embeddings for semantic search |
| `ANTHROPIC_API_KEY` | No | — | AI extraction (future) |
| `CORS_ORIGINS` | No | `localhost:3000` | Frontend origins |

## Hebrew Text Handling

- **Encoding:** Always UTF-8. Never normalize Hebrew spelling.
- **Cantillation:** Preserved when available from Sefaria.
- **RTL:** First-class in frontend (planned). API returns raw Hebrew text.
- **Search:** Neo4j full-text indexes treat cantillation as token boundaries. For pure Hebrew search, clients may strip cantillation before querying.

## 7-Phase Implementation Roadmap

| Phase | Weeks | Deliverables | Gate |
|-------|-------|-------------|------|
| **1: Architecture** | 1-2 | Design docs, Docker Compose, health checks | All services start |
| **2: Data Model** | 3-4 | Neo4j/PostgreSQL/Qdrant schemas, seed data | Schema tests pass |
| **3: Import Pipeline** | 5-7 | Sefaria ingestion, 100K+ nodes, 0 integrity violations | Tanakh + Mishnah imported |
| **4: Knowledge Extraction** | 8-10 | AI extraction service, human validation queue | Precision > 80% |
| **5: Visualization** | 11-13 | 5 graph views, 60fps at 1K nodes | All views functional |
| **6: AI Discovery** | 14-16 | Cross-references, gematria, semantic similarity | 50K+ discovered relationships |
| **7: Advanced Intelligence** | 17-20 | All 7 graph layers, load testing, production guide | 100 concurrent users |

---

## Ontology Research

Before a single production feature was built, the ontology was stress-tested with **500 real Torah concepts** across 5 domains. The result:

- **V1:** 70% modeled cleanly — exposed multi-domain and experiential failures
- **V2:** 90% modeled cleanly — added dimensional layers, worldviews, experiential annex
- **V3:** **100% modeled cleanly** — added meta-ontological layer for self-referential and transcendent concepts

The ontology is a **multi-dimensional, self-reflective, process-oriented, negative-capable formal system** with 6,000+ entities and 22,000+ relationships.

---

## Critical Rules

- **Never invent Torah sources.** Every relationship requires a real citation.
- **Never fabricate citations.** Exact references only.
- **Always preserve exact references.** Book, chapter, verse, page, daf.
- **Always track provenance.** Model, prompt, temperature, validator.
- **Distinguish:** Explicit source | Derived relationship | AI-inferred relationship.

---

## License

This is a research and open-source project. Data sources (Sefaria) have their own licenses. All original ontology and software work is released under the MIT License.

---

> *"The Torah is a living graph. We are only mapping the connections that have always been there."*
