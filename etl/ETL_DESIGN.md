# Torah Knowledge Graph — ETL Pipeline Design

## 1. Overview

This document specifies the complete Extract-Transform-Load (ETL) pipeline for the Torah Knowledge Graph platform. The pipeline ingests structured and semi-structured Torah data from multiple sources, normalizes it into a canonical schema, validates it for integrity and quality, and loads it into the graph database (Neo4j), relational store (PostgreSQL), and vector index (Qdrant).

### 1.1 Design Goals
- **Completeness**: Ingest all available structured Torah data from primary sources.
- **Correctness**: Preserve textual accuracy, provenance, and referential integrity.
- **Scalability**: Handle batch sizes from single texts to full library exports (500K+ texts).
- **Observability**: Every job, failure, and data quality anomaly is logged and alerted.
- **Extensibility**: New sources and formats can be added without rewriting core logic.

### 1.2 Sources
| Source | Format | API/Export | Volume |
|--------|--------|------------|--------|
| Sefaria | JSON (REST) | `/api/texts/`, `/api/index/`, `/api/links/` | ~300K texts |
| Sefaria Export | JSON/CSV | Bulk ZIP dumps | ~1 TB uncompressed |
| Open Torah Datasets | XML, TEI, plain text | GitHub repositories | Variable |

### 1.3 Target Schema
Data lands in three stores, coordinated by a shared canonical entity identifier:
- **Neo4j**: Graph nodes (`Text`, `Person`, `Place`, `Concept`, `Mitzvah`, `Commentary`) and edges (`CITES`, `COMMENTARY_ON`, `MENTIONS`, `AUTHORED_BY`).
- **PostgreSQL**: Raw import tables, audit log, job tracking, and normalized metadata.
- **Qdrant**: Vector embeddings of text segments for semantic search and AI extraction context.

---

## 2. Sefaria API Ingestion Pipeline

### 2.1 Rate Limiting
Sefaria requests a **maximum of 1 request per second** on all public endpoints. The pipeline enforces this via a token-bucket rate limiter backed by Redis.

**Implementation:**
```python
# Conceptual implementation
class SefariaRateLimiter:
    def __init__(self, redis_client: redis.Redis, rate: float = 1.0, burst: int = 3):
        self.redis = redis_client
        self.rate = rate        # requests per second
        self.burst = burst      # max burst before throttling

    async def acquire(self, key: str = "sefaria:api") -> None:
        """Block until a token is available."""
        while True:
            now = time.monotonic()
            pipe = self.redis.pipeline()
            pipe.hmget(key, "tokens", "last_update")
            result = await pipe.execute()
            tokens = float(result[0][0] or self.burst)
            last_update = float(result[0][1] or now)

            elapsed = now - last_update
            tokens = min(self.burst, tokens + elapsed * self.rate)

            if tokens >= 1.0:
                pipe.hset(key, mapping={"tokens": tokens - 1.0, "last_update": now})
                await pipe.execute()
                return
            await asyncio.sleep(max(0.01, (1.0 - tokens) / self.rate))
```

**Policy:**
- All API workers share the same Redis-backed bucket (`sefaria:api`).
- Burst of 3 allows short spikes; steady state is 1 req/sec.
- If the bucket is empty, workers sleep with exponential backoff up to 5 seconds.
- **Hard ceiling**: Never exceed 1 req/sec averaged over any 60-second window.

### 2.2 Pagination Handling
Sefaria endpoints return variable-size payloads. Pagination strategy varies by endpoint.

**Endpoint: `/api/texts/{ref}`**
- Returns a single text unit (chapter, section, or paragraph).
- No traditional pagination; references are hierarchical (`Genesis.1`, `Genesis.1.1`).
- **Strategy**: Walk the index tree depth-first using `/api/index/{title}` to discover available depth levels, then enumerate all refs.

**Endpoint: `/api/index/{title}`**
- Returns metadata about a text: depth, length, section names, authors, etc.
- **Strategy**: Called once per text title before bulk text fetching.

**Endpoint: `/api/links/{ref}`**
- Returns linked texts (commentaries, cross-references) for a given ref.
- Supports `?page=0&page_size=200`.
- **Strategy**: Paginate with `page_size=200` until `count` in response is exhausted.
- Total link count is pre-fetched via `?page=0&page_size=0` to estimate job size.

**Reference Enumeration Algorithm:**
```python
async def enumerate_refs(title: str) -> List[str]:
    index = await fetch_index(title)
    depth = index["schema"]["depth"]  # e.g., 2 for Chumash (book, chapter)
    lengths = index["schema"]["lengths"]  # e.g., [50, ...] for Genesis
    refs = []
    def walk(current: List[int], level: int):
        if level == depth:
            refs.append(format_ref(title, current))
            return
        max_at_level = lengths[level] if level < len(lengths) else 1
        for i in range(1, max_at_level + 1):
            walk(current + [i], level + 1)
    walk([], 0)
    return refs
```

### 2.3 Endpoint Mapping

| Endpoint | Method | Purpose | Pipeline Stage |
|----------|--------|---------|----------------|
| `/api/index/{title}` | GET | Text metadata, structure, authors | Discovery |
| `/api/texts/{ref}` | GET | Actual Hebrew/English text content | Extraction |
| `/api/texts/{ref}?context=1` | GET | Text with surrounding context | Context enrichment |
| `/api/links/{ref}` | GET | Commentaries and cross-references | Link extraction |
| `/api/words/{word}` | GET | Word-level data (optional) | Lexical enrichment |

**Data Flow:**
1. **Discovery Worker**: Fetches `/api/index/{title}` for all texts in the catalog, stores metadata in PostgreSQL (`raw_index` table).
2. **Text Worker**: Consumes index records from a Redis queue, fetches `/api/texts/{ref}` for each leaf ref, stores raw JSON in PostgreSQL (`raw_texts`) and S3.
3. **Link Worker**: After text ingestion, fetches `/api/links/{ref}` for each ref, stores in `raw_links`.

### 2.4 Error Handling and Retry Logic

**Retry Categories:**
| HTTP Status | Category | Behavior | Max Retries | Backoff |
|-------------|----------|----------|-------------|---------|
| 429 | Rate limit | Read `Retry-After`, wait, re-acquire token | Unlimited | As header |
| 502, 503, 504 | Transient | Exponential backoff | 5 | 2^attempt * 1s |
| 404 | Missing ref | Log as `MISSING_REF`, skip | 1 | None |
| 400 | Bad request | Log as `INVALID_REF`, quarantine | 0 | None |
| Timeout | Network | Exponential backoff | 5 | 2^attempt * 1s |

**Circuit Breaker:**
- If error rate exceeds 10% over a 5-minute window, circuit opens for 60 seconds.
- During open circuit, jobs are requeued with visibility delay.
- After 60 seconds, half-open state allows 1 probe request; success closes the circuit.

**Dead Letter Queue (DLQ):**
- After max retries, jobs move to `sefaria_dlq` Redis stream.
- DLQ consumer runs daily, attempts one manual retry, then alerts operators if still failing.
- DLQ entries include: original request URL, all retry timestamps, final exception, and stack trace.

### 2.5 Incremental Sync Strategy

**Watermark-Based Sync:**
- PostgreSQL table `sync_watermarks` tracks the last successful sync timestamp per source and text category.
- Sefaria does not expose a native "modified since" field on all endpoints, so we use a hybrid approach.

**Hybrid Strategy:**
1. **Index Sync (Daily)**: Full re-fetch of `/api/index/{title}` for all texts. Compare `lastModified` timestamp (when available) or structural hash (MD5 of lengths array) against the previous sync. Only changed texts are re-queued for text extraction.
2. **Text Sync (Weekly)**: For texts marked changed by index sync, re-fetch all refs. For unchanged texts, spot-check 1% of refs to detect unannounced changes.
3. **Link Sync (Bi-weekly)**: Links are highly dynamic. Full re-fetch of `/api/links/{ref}` for all refs, but only for texts in the top 20% by commentary count (determined heuristically).

**Version Tracking:**
- Every text record stores `ingested_at`, `sync_version` (monotonic integer per text), and `content_hash` (SHA-256 of normalized content).
- On re-ingestion, if `content_hash` matches the previous version, the record is a no-op (only `last_seen_at` is updated).
- If content changed, a new version is inserted; Neo4j is updated with a `replaced_by` edge from old to new node.

---

## 3. Sefaria Export Ingestion

### 3.1 Export Format Parsing
Sefaria publishes bulk exports as ZIP archives containing JSON and CSV files.

**Export Structure (typical):**
```
sefaria-export/
  texts/
    Tanakh/
      Genesis.json          # Array of chapter objects
      Exodus.json
    Talmud/
      Bavli/
        Berakhot.json       # Nested by daf, amud
  links/
    all_links.csv           # source, target, type, category
  index/
    all_index.json          # Metadata for all texts
  lexicon/
    ...
```

**JSON Format (texts):**
```json
{
  "title": "Genesis",
  "heTitle": "בראשית",
  "text": [
    ["בְּרֵאשִׁית בָּרָא אֱלֹהִים...", "..."],
    ["..."]
  ],
  "heVersionSource": "...",
  "versionTitle": "...",
  "language": "he"
}
```

**CSV Format (links):**
```csv
source,target,type,category
Genesis 1:1,Rashi on Genesis 1:1,commentary,Commentary
```

**Parsing Strategy:**
- **JSON**: Use `ijson` or `orjson` for streaming parse of large files (>100MB). Never load entire file into memory.
- **CSV**: Use `polars` lazy reader with `streaming=True` for out-of-core processing.
- **ZIP**: Extract to temporary directory; process files one at a time; delete temp files immediately after ingestion.

### 3.2 Bulk Loading Strategy

**Staging Pattern:**
1. **Raw Load**: Ingest export files into PostgreSQL staging tables (`staging_texts`, `staging_links`) with no foreign key constraints, using `COPY FROM` for maximum throughput.
2. **Transform**: Run SQL transformations in PostgreSQL to normalize staging data into the canonical schema.
3. **Validate**: Run referential integrity and data quality checks.
4. **Load**: Upsert validated records into Neo4j and Qdrant.

**Throughput Targets:**
| Stage | Target Rate | Bottleneck |
|-------|-------------|------------|
| Raw PostgreSQL load | 10K records/sec | Disk I/O |
| Neo4j upsert | 2K nodes/sec | Network + Cypher parse |
| Qdrant embed + index | 500 texts/sec | GPU embedding model |

**Batch Sizes:**
- PostgreSQL: 10K rows per `COPY` batch.
- Neo4j: 1K nodes per `UNWIND` Cypher batch.
- Qdrant: 100 points per `upsert` call (limited by embedding model batch size).

### 3.3 Version Tracking
Every bulk export has a version identifier derived from the export timestamp or Sefaria release tag.

**Version Table (`export_versions`):**
| Column | Type | Description |
|--------|------|-------------|
| `version_id` | UUID | Primary key |
| `source` | TEXT | `sefaria_export` |
| `export_date` | DATE | Date of export |
| `export_tag` | TEXT | Git tag or version string |
| `downloaded_at` | TIMESTAMP | When we fetched it |
| `ingested_at` | TIMESTAMP | When ingestion completed |
| `record_count` | BIGINT | Total records ingested |
| `checksum` | TEXT | SHA-256 of the ZIP file |

**Change Detection:**
- Compute a Merkle tree over all text content hashes in the export.
- If the root hash matches the previous export, skip ingestion entirely.
- If it differs, diff at the branch level to identify which texts changed, then ingest only changed texts.

---

## 4. Open Torah Dataset Adapters

### 4.1 GitHub Dataset Discovery
A registry of known Torah datasets is maintained in `datasets.yml`. A discovery crawler periodically scans GitHub for new repositories matching Torah-related keywords.

**Discovery Configuration (`datasets.yml`):**
```yaml
datasets:
  - name: open_tanakh
    source: github
    repo: open-scriptures/morphhb
    format: xml
    license: CC-BY-SA
    refresh_interval: weekly
    adapter: morphhb_adapter

  - name: sefaria_export_mirror
    source: github
    repo: Sefaria/Sefaria-Export
    format: json
    license: CC-BY-SA
    refresh_interval: daily
    adapter: sefaria_export_adapter
```

**Discovery Crawler:**
- Queries GitHub Search API for topics: `torah`, `tanakh`, `talmud`, `hebrew-bible`.
- Filters by: open source license, non-fork, updated within 12 months, >10 stars.
- Proposes new entries via PR to `datasets.yml`; human approval required before ingestion.

### 4.2 Format Normalization (XML, TEI, Plain Text)

**Adapter Interface:**
```python
class TorahDatasetAdapter(Protocol):
    def parse(self, raw_path: Path) -> Iterator[CanonicalTextSegment]: ...
    def normalize_hebrew(self, text: str) -> str: ...
    def extract_metadata(self, raw: dict) -> TextMetadata: ...
```

**XML/TEI Adapter:**
- Uses `lxml.iterparse` for streaming SAX-style parsing of large XML files.
- TEI elements mapped to canonical fields:
  - `<teiHeader>` / `<titleStmt>` / `<title>` → `title`, `heTitle`
  - `<text>` / `<body>` / `<div>` → hierarchical text structure
  - `<ab>` or `<p>` with `xml:lang="he"` → Hebrew content
- Normalization strips TEI-specific markup, preserves paragraph boundaries.

**Plain Text Adapter:**
- Expects a manifest file (`manifest.json`) describing the text structure.
- Plain text files are chunked by paragraph (double newline) or by manifest-specified boundaries.
- No markup to strip; minimal transformation.

**Normalization Pipeline:**
1. **Decode**: Ensure UTF-8; detect and convert legacy encodings (Windows-1255, ISO-8859-8).
2. **Strip markup**: Remove XML tags, HTML entities, control characters.
3. **Normalize whitespace**: Collapse multiple spaces/newlines; preserve paragraph structure.
4. **Hebrew normalization**: See Section 5.1.
5. **Canonical encoding**: Output as JSON Lines (`.jsonl`) with one record per text segment.

### 4.3 Schema Mapping to Neo4j Nodes

Every normalized text segment becomes a graph node with standardized properties.

**Node Mapping:**
| Canonical Field | Neo4j Property | Type |
|-----------------|----------------|------|
| `canonical_ref` | `ref` | String (e.g., `Genesis.1.1`) |
| `hebrew_text` | `textHe` | String |
| `english_text` | `textEn` | String (nullable) |
| `text_title` | `title` | String |
| `hebrew_title` | `titleHe` | String |
| `category` | `category` | String (e.g., `Tanakh`, `Talmud`) |
| `author` | `author` | String |
| `source_dataset` | `dataset` | String |
| `ingested_at` | `ingestedAt` | DateTime |
| `content_hash` | `contentHash` | String (SHA-256) |

**Label Assignment:**
- Base label: `Text`
- Additional label by category: `Tanakh`, `Talmud`, `Halakhah`, etc.
- Additional label by source: `SefariaText`, `OpenTorahText`

---

## 5. Data Transformation Rules

### 5.1 Hebrew Text Normalization
Hebrew text in the wild varies in spelling, vocalization, and encoding. Normalization ensures that texts from different sources are comparable and that reference parsing works reliably.

**Normalization Pipeline:**
1. **Unicode Normalization**: Apply NFC to combine decomposed characters.
2. **Niqqud (Vowel) Handling**:
   - **Preservation mode** (default for Tanakh, Siddur): Retain all niqqud marks.
   - **Stripping mode** (default for Talmud, Halakhah): Remove all niqqud and cantillation marks (`U+0591`–`U+05AF`, `U+05BF`, `U+05C0`, `U+05C4`).
   - Configurable per category in `hebrew_normalization.yml`.
3. **Spelling Standardization**:
   - Normalize final forms (`ך`, `ם`, `ן`, `ף`, `ץ`) vs medial forms (`כ`, `מ`, `נ`, `פ`, `צ`). Context-aware using word-position heuristics.
   - Normalize optional vowel letters (mater lectionis): `א` vs `ה` vs `י` vs `ו` according to Biblical Hebrew standard (configurable per era: Biblical, Mishnaic, Medieval).
4. **Whitespace**: Collapse multiple spaces; trim leading/trailing whitespace.
5. **Directionality**: Ensure RTL mark (`U+200F`) is present at the start of Hebrew-only strings for proper rendering.

**Implementation:**
```python
import unicodedata
import regex

NIQQUD_RANGE = regex.compile(r'[֑-ֿ֯׀ׄ]+')

def normalize_hebrew(text: str, mode: str = "strip_niqqud") -> str:
    text = unicodedata.normalize("NFC", text)
    if mode == "strip_niqqud":
        text = NIQQUD_RANGE.sub("", text)
    # Additional rules for spelling standardization
    return text.strip()
```

### 5.2 Reference Parsing
Torah references follow hierarchical patterns. The parser converts human-readable strings into structured objects.

**Supported Formats:**
- `"Genesis 1:1"` → `{book: "Genesis", chapter: 1, verse: 1}`
- `"Genesis 1:1-3"` → range `{book: "Genesis", chapter: 1, start_verse: 1, end_verse: 3}`
- `"Rashi on Genesis 1:1"` → `{commentary: "Rashi", base_text: "Genesis", chapter: 1, verse: 1}`
- `"Shabbat 2a"` → `{tractate: "Shabbat", daf: 2, amud: "a"}`
- `"Pesachim 10b:3"` → `{tractate: "Pesachim", daf: 10, amud: "b", line: 3}`
- `"Mishnah Berurah 1:1"` → `{work: "Mishnah_Berurah", section: 1, subsection: 1}`

**Parser Architecture:**
1. **Tokenization**: Split on spaces, colons, periods, hyphens.
2. **Book Resolution**: Match tokens against the canonical book index (from PostgreSQL `canonical_books` table). Supports Hebrew aliases (`בראשית` → `Genesis`).
3. **Structure Resolution**: Use the text's `depth` and `sectionNames` from index metadata to assign numbers to the correct structural level.
4. **Range Expansion**: Split ranges into individual refs for graph linking; store the range as a property on the parent query.

**Error Handling:**
- Unresolvable refs are logged to `parse_errors` table with the raw string, attempted parser, and confidence score.
- Fuzzy matching with Levenshtein distance <= 2 is attempted for misspelled book names.

### 5.3 Author Attribution Normalization
Authors are referenced inconsistently across sources (e.g., "Rashi", "R. Shlomo Yitzchaki", "רש"י"). Normalization produces a canonical author entity.

**Canonical Author Schema:**
| Field | Description |
|-------|-------------|
| `canonical_name` | Primary English name (e.g., `Rashi`) |
| `canonical_name_he` | Primary Hebrew name (e.g., `רש"י`) |
| `aliases` | Array of known aliases |
| `era` | `Tannaim`, `Amoraim`, `Rishonim`, `Acharonim`, `Modern` |
| `birth_year` | Approximate birth year (Gregorian) |
| `death_year` | Approximate death year (Gregorian) |
| `geography` | Primary geographic association |

**Normalization Rules:**
1. **Alias Resolution**: Maintain an `author_aliases` table mapping 500+ known aliases to canonical IDs.
2. **Era Inference**: If birth/death years are unknown, infer from the type of work (e.g., Talmud commentaries → `Rishonim` or `Acharonim`).
3. **Disambiguation**: If two authors share a name (e.g., multiple "Rabbi Yosef"), use geographic or temporal qualifiers.
4. **Unknown Authors**: Assign to a placeholder `UnknownAuthor` node with a `source_hint` property; queue for human review.

---

## 6. Data Validation Rules

### 6.1 Schema Compliance Checks
Every record must conform to the canonical schema before loading into Neo4j.

**Validation Layers:**
1. **JSON Schema Validation** (`jsonschema`): Validate raw API responses against versioned schemas.
2. **Pydantic Models**: All records are parsed into strict Pydantic models with typed fields.
3. **Custom Validators**:
   - `ref` must match the canonical reference regex for its category.
   - `hebrew_text` must contain only valid Unicode Hebrew ranges plus punctuation.
   - `english_text` must not contain RTL override characters unless properly scoped.

**Validation Results:**
- `VALID`: Passes all checks.
- `WARNING`: Passes core checks but has non-critical issues (e.g., empty `english_text`). Loaded with `validation_status: warning`.
- `INVALID`: Fails critical checks. Quarantined in `validation_quarantine` table; not loaded.

### 6.2 Referential Integrity
The graph must maintain logical consistency: a commentary cannot cite a base text that does not exist.

**Integrity Rules:**
1. **Book-before-chapter**: A `Text` node with `ref: "Genesis.1.1"` requires a parent `Text` node with `ref: "Genesis.1"` and ultimately `"Genesis"`.
2. **Link targets exist**: Every `CITES` or `COMMENTARY_ON` edge must point to an existing node (or a node scheduled for creation in the same batch).
3. **Author exists**: Every `AUTHORED_BY` edge must point to an existing `Person` node.
4. **Category exists**: The `category` property must match an entry in the `canonical_categories` table.

**Enforcement Strategy:**
- **Batch validation**: Before Neo4j upsert, build an in-memory set of all refs in the batch. Verify that all link targets are either already in Neo4j (via `MATCH` probe) or present in the batch.
- **Deferred constraints**: If a link target is missing, the edge is queued in `deferred_edges` with a TTL of 7 days. A daily job attempts to resolve deferred edges.

### 6.3 Duplicate Detection

**Duplicate Types:**
1. **Exact duplicates**: Same `content_hash` and `ref`.
2. **Near-duplicates**: Same `ref`, different `content_hash` but >95% text similarity (Levenshtein ratio).
3. **Cross-source duplicates**: Same text from Sefaria API and Sefaria Export (expected; handled by version tracking).

**Detection Strategy:**
- Exact duplicates: Blocked by unique constraint on `(Text {ref, contentHash})`.
- Near-duplicates: Detected during transform stage using MinHash LSH on 5-gram shingles. Candidates are flagged for human review.
- Cross-source: Resolved by `source_dataset` priority (Sefaria API > Sefaria Export > Open Torah), with the lower-priority version stored as an `ALTERNATE_VERSION` edge.

---

## 7. Pipeline Orchestration with Celery + Redis

### 7.1 Architecture

**Components:**
| Component | Technology | Role |
|-----------|------------|------|
| Task Queue | Redis Streams + Celery | Distribute work to workers |
| Workers | Celery (async/gevent pool) | Execute fetch, parse, transform, load |
| Scheduler | Celery Beat | Trigger periodic sync jobs |
| Result Backend | Redis | Store task states and metadata |
| Orchestrator | Celery Canvas (chains, chords, groups) | Compose multi-stage workflows |

**Worker Types:**
| Worker | Queue | Concurrency | Purpose |
|--------|-------|-------------|---------|
| `discovery` | `discovery` | 2 | Index/catalog crawling |
| `api_fetch` | `api_fetch` | 1 (rate-limited) | Sefaria API calls |
| `export_fetch` | `export_fetch` | 4 | Bulk export download/processing |
| `transform` | `transform` | 8 | Normalization and parsing |
| `validate` | `validate` | 4 | Schema and integrity checks |
| `load_neo4j` | `load_neo4j` | 4 | Neo4j batch upserts |
| `load_qdrant` | `load_qdrant` | 2 | Embedding + vector upsert |

### 7.2 Workflow Definitions

**Full Sync Workflow (Sefaria API):**
```python
from celery import chain, group, chord

full_sync = chain(
    discovery_task.s(),                          # Fetch all indices
    group(text_fetch_task.s(ref) for ref in refs), # Parallel text fetch
    group(link_fetch_task.s(ref) for ref in refs), # Parallel link fetch
    transform_batch_task.s(),                     # Normalize all
    validate_batch_task.s(),                      # Check integrity
    chord(
        group(neo4j_upsert_task.s(batch) for batch in neo4j_batches),
        group(qdrant_upsert_task.s(batch) for batch in qdrant_batches),
    ),
    sync_complete_task.s(),                       # Update watermark
)
```

**Incremental Sync Workflow:**
- Uses the same pipeline but with a pre-filter step that only enqueues refs changed since the last watermark.

### 7.3 Configuration

**Celery Config (`celeryconfig.py`):**
```python
broker_url = "redis://redis:6379/0"
result_backend = "redis://redis:6379/0"
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
task_track_started = True
task_time_limit = 300  # 5 minutes per task
task_soft_time_limit = 240
worker_prefetch_multiplier = 1  # Critical for rate-limited API worker
task_acks_late = True
```

---

## 8. Monitoring and Alerting

### 8.1 Metrics
Every pipeline stage emits metrics to Prometheus.

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `etl_records_processed_total` | Counter | `stage`, `source`, `status` | Records through each stage |
| `etl_records_per_second` | Gauge | `stage`, `source` | Throughput |
| `etl_job_duration_seconds` | Histogram | `job_type`, `status` | End-to-end job time |
| `etl_queue_depth` | Gauge | `queue_name` | Pending tasks |
| `etl_api_rate_limited_total` | Counter | `endpoint` | Rate limit hits |
| `etl_validation_failed_total` | Counter | `check_type`, `severity` | Validation failures |
| `etl_deferred_edges_total` | Gauge | - | Unresolved edges |

### 8.2 Health Checks
| Check | Endpoint | Frequency | Failure Action |
|-------|----------|-----------|----------------|
| Redis connectivity | `redis.ping()` | Every 10s | Alert after 3 failures |
| PostgreSQL connectivity | `SELECT 1` | Every 10s | Alert after 3 failures |
| Neo4j connectivity | `CALL dbms.components()` | Every 30s | Alert after 2 failures |
| Qdrant connectivity | `GET /healthz` | Every 30s | Alert after 2 failures |
| Worker liveness | Celery `ping()` | Every 60s | Restart after 2 failures |

### 8.3 Alerting Rules (Prometheus Alertmanager)
| Alert | Condition | Severity | Escalation |
|-------|-----------|----------|------------|
| `ETLHighErrorRate` | `etl_validation_failed_total / etl_records_processed_total > 0.05` for 5m | Warning | Slack #etl-alerts |
| `ETLJobStalled` | `etl_queue_depth > 1000` and `etl_records_per_second == 0` for 10m | Critical | PagerDuty + Slack |
| `ETLApiRateLimited` | `etl_api_rate_limited_total` increased by >10 in 1m | Warning | Slack #etl-alerts |
| `ETLNeo4jLoadSlow` | `etl_job_duration_seconds{job_type="neo4j_upsert", quantile="0.99"} > 60` | Warning | Slack |
| `ETLDeferredEdgesGrowing` | `etl_deferred_edges_total` increased by >100 in 1h | Warning | Slack |

### 8.4 Dashboards
Grafana dashboards are provisioned in `infrastructure/grafana/dashboards/etl.json`.
- **Overview**: Job counts, throughput, error rates, queue depths.
- **Source Health**: Per-source ingestion status, last sync time, record counts.
- **Data Quality**: Validation pass/fail rates, top failure reasons, quarantine size.
- **Graph Growth**: Node and edge counts by label, daily growth rate.

### 8.5 Logging
- Structured JSON logs via `structlog`.
- Every log entry includes: `job_id`, `task_id`, `source`, `ref` (if applicable), `stage`, `duration_ms`, `record_count`.
- Logs shipped to Loki for aggregation and search.

---

## 9. Security and Compliance

### 9.1 Data Privacy
- No personal user data is ingested; only public domain Torah texts and metadata.
- Sefaria API terms of service are respected (rate limits, attribution).

### 9.2 Secrets Management
- API keys (if needed for premium endpoints) stored in HashiCorp Vault or AWS Secrets Manager.
- Workers read secrets at startup; no secrets in code or environment variables except Vault token.

### 9.3 Audit Trail
- `audit_log` table in PostgreSQL records every write to Neo4j: `job_id`, `user/system`, `action`, `target_node`, `timestamp`, `diff`.
- Immutable; append-only.

---

## 10. Appendix: Data Model Quick Reference

### PostgreSQL Tables (ETL-specific)
| Table | Purpose |
|-------|---------|
| `raw_index` | Sefaria index metadata |
| `raw_texts` | Raw text JSON from API/export |
| `raw_links` | Raw link data |
| `staging_texts` | Pre-transform bulk load staging |
| `staging_links` | Pre-transform link staging |
| `canonical_texts` | Normalized text segments |
| `canonical_links` | Normalized graph edges |
| `canonical_authors` | Normalized author entities |
| `canonical_books` | Book reference catalog |
| `sync_watermarks` | Last sync timestamp per source |
| `export_versions` | Bulk export version tracking |
| `validation_quarantine` | Failed validation records |
| `deferred_edges` | Unresolved graph edges |
| `audit_log` | Immutable audit trail |
| `parse_errors` | Reference parsing failures |
| `author_aliases` | Author name alias mappings |

### Neo4j Constraints
```cypher
CREATE CONSTRAINT text_ref_hash IF NOT EXISTS
FOR (t:Text) REQUIRE (t.ref, t.contentHash) IS UNIQUE;

CREATE CONSTRAINT person_name IF NOT EXISTS
FOR (p:Person) REQUIRE p.canonicalName IS UNIQUE;

CREATE CONSTRAINT category_name IF NOT EXISTS
FOR (c:Category) REQUIRE c.name IS UNIQUE;
```

---

*Document Version: 1.0*
*Last Updated: 2026-06-04*
*Maintainer: Torah Knowledge Graph Engineering Team*
