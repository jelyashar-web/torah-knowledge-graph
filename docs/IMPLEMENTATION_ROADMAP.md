# Torah Knowledge Graph — Implementation Roadmap

## 1. Overview

This document provides a step-by-step implementation plan for the Torah Knowledge Graph platform. The roadmap is organized into seven phases, spanning 20 weeks, with clear deliverables, acceptance criteria, and milestone gates for each phase.

### 1.1 Project Vision
Build a comprehensive, AI-augmented knowledge graph of Torah, Talmud, and Jewish textual tradition. The platform will serve researchers, educators, and learners by providing structured access to entities, relationships, and insights across the corpus of Jewish literature.

### 1.2 Guiding Principles
- **Data quality over quantity**: A smaller, accurate graph is better than a large, noisy one.
- **Human-in-the-loop from day one**: AI extraction is powerful but must be validated by domain experts.
- **Incremental delivery**: Each phase produces a working, demoable system.
- **Observability everywhere**: Every pipeline stage is monitored, logged, and alerted.

---

## 2. Technology Stack Versions

The following stack versions are locked for the initial 20-week implementation. Upgrades are allowed between phases if they do not block dependent work.

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Graph Database** | Neo4j Community/Enterprise | 5.x | Core knowledge graph storage |
| **Relational Database** | PostgreSQL | 16.x | Metadata, audit log, job tracking |
| **Vector Database** | Qdrant | 1.x | Semantic search, embedding storage |
| **Cache / Queue** | Redis | 7.x | Rate limiting, Celery broker, result backend |
| **Task Orchestration** | Celery | 5.3.x | Distributed task queue |
| **Backend Framework** | FastAPI | 0.110+ | REST and GraphQL API |
| **Language** | Python | 3.12+ | ETL, AI extraction, backend services |
| **Frontend Framework** | React | 18.x | Web application |
| **Graph Visualization** | D3.js + Cytoscape.js | Latest | Interactive graph views |
| **LLM API** | Anthropic Claude | 4.x | Entity and relationship extraction |
| **Embeddings** | OpenAI / Local | text-embedding-3-large or fine-tuned | Text vectorization |
| **Containerization** | Docker + Docker Compose | 25.x | Local development and deployment |
| **Orchestration** | Kubernetes (prod) | 1.29+ | Production deployment (Phase 7) |
| **Monitoring** | Prometheus + Grafana | Latest | Metrics and dashboards |
| **Logging** | Loki + Grafana | Latest | Log aggregation |
| **Alerting** | Prometheus Alertmanager | Latest | Alert routing |
| **Infrastructure** | Terraform | 1.7+ | IaC for cloud resources |

---

## 3. Phase Breakdown

### Phase 1: Architecture (Weeks 1–2)

**Goal**: Establish the technical foundation. All services run locally in Docker Compose with health checks passing.

**Deliverables:**
1. All design documents completed and approved:
   - ETL Pipeline Design (`etl/ETL_DESIGN.md`)
   - AI Extraction Design (`ai-extraction/AI_EXTRACTION_DESIGN.md`)
   - Graph Data Model (`databases/GRAPH_MODEL.md`)
   - API Design (`backend/API_DESIGN.md`)
   - Frontend Design (`frontend/FRONTEND_DESIGN.md`)
   - Infrastructure Design (`infrastructure/INFRA_DESIGN.md`)
2. Docker Compose environment running all core services:
   - Neo4j, PostgreSQL, Qdrant, Redis, FastAPI backend, React frontend
3. CI/CD pipeline configured (GitHub Actions):
   - Lint, type check, unit tests on every PR
   - Docker image build and push on merge to `main`
4. Development environment documentation (`docs/DEVELOPMENT.md`):
   - Setup instructions, environment variables, common commands
5. Monorepo structure established with:
   - `backend/`, `frontend/`, `etl/`, `ai-extraction/`, `databases/`, `infrastructure/`, `docs/`

**Acceptance Criteria:**
- [ ] `docker compose up` starts all 6 services without errors
- [ ] Health check endpoints return HTTP 200 for all services
- [ ] CI pipeline passes on `main` branch (lint, test, build)
- [ ] New developer can go from `git clone` to running stack in <30 minutes
- [ ] All design documents are reviewed and signed off by the tech lead

**Milestone Gate: Architecture Review**
- Gate Date: End of Week 2
- Gate Criteria: All acceptance criteria above must pass
- Exit Action: Proceed to Phase 2 or halt and fix architecture issues

---

### Phase 2: Data Model (Weeks 3–4)

**Goal**: Deploy the canonical data model across all three databases. Schema validation tests pass.

**Deliverables:**
1. Neo4j schema deployed:
   - Node labels: `Text`, `Person`, `Place`, `Concept`, `Mitzvah`, `Event`, `Commentary`, `Category`
   - Relationship types: `CITES`, `COMMENTARY_ON`, `MENTIONS`, `AUTHORED_BY`, `TEACHES`, `RELATED_TO`, `OCCURRED_AT`, `PARTICIPATED_IN`, `REQUIRES`, `FOLLOWS_FROM`, `OPPOSES`
   - Constraints: Unique constraints on `(Text {ref, contentHash})`, `(Person {canonicalName})`, `(Category {name})`
   - Indexes: Full-text index on `Text.textHe` and `Text.textEn`
2. PostgreSQL schema migrated:
   - Raw staging tables (`raw_index`, `raw_texts`, `raw_links`)
   - Canonical tables (`canonical_texts`, `canonical_authors`, `canonical_books`, `canonical_links`)
   - System tables (`sync_watermarks`, `export_versions`, `validation_quarantine`, `deferred_edges`, `audit_log`, `parse_errors`, `author_aliases`, `extraction_provenance`, `review_queue`, `rejected_extractions`, `model_feedback`)
   - Alembic migration scripts committed
3. Qdrant collections created:
   - Collection `torah_texts` with vector size 3072 (text-embedding-3-large)
   - Payload schema: `ref`, `title`, `category`, `author`, `language`
   - HNSW index configured with `m=16`, `ef_construct=100`
4. Schema validation test suite:
   - pytest suite asserting all constraints, indexes, and foreign keys exist
   - Test data fixtures for each entity type

**Acceptance Criteria:**
- [ ] All Alembic migrations run successfully forward and backward
- [ ] Neo4j constraint creation scripts execute without error
- [ ] Qdrant collection creation returns success and schema matches spec
- [ ] Schema validation test suite passes (100% of tests green)
- [ ] Sample data can be inserted into all three stores and round-tripped

**Milestone Gate: Data Model Review**
- Gate Date: End of Week 4
- Gate Criteria: Schema validation tests pass; sample data round-trips correctly
- Exit Action: Proceed to Phase 3 or fix schema issues

---

### Phase 3: Import Pipeline (Weeks 5–7)

**Goal**: Sefaria ingestion pipeline is operational. Initial dataset loaded with referential integrity verified.

**Deliverables:**
1. Sefaria API ingestion pipeline:
   - Rate limiter (1 req/sec) with Redis token bucket
   - Pagination handlers for `/api/texts/`, `/api/index/`, `/api/links/`
   - Retry logic with exponential backoff and circuit breaker
   - Incremental sync strategy with watermark tracking
2. Sefaria Export ingestion pipeline:
   - ZIP download and streaming parse (JSON + CSV)
   - Bulk load into PostgreSQL staging tables via `COPY FROM`
   - Version tracking with Merkle tree diff
3. Data transformation layer:
   - Hebrew text normalization (NFC, niqqud stripping, spelling standardization)
   - Reference parser ("Genesis 1:1" → structured) with fuzzy matching
   - Author attribution normalization with alias resolution
4. Data validation layer:
   - Schema compliance checks (Pydantic models + JSON schema)
   - Referential integrity validation (book-before-chapter, link targets exist)
   - Duplicate detection via content hash and MinHash LSH
5. Pipeline orchestration:
   - Celery workers for each stage (discovery, fetch, transform, validate, load)
   - Celery Beat scheduler for periodic sync jobs
   - Redis Streams for queue management
6. Initial dataset:
   - Full Tanakh (Hebrew + English) + major commentaries (Rashi, Ramban, Ibn Ezra)
   - Full Mishnah + select Talmud tractates (Berakhot, Shabbat, Eruvin)
   - Target: 100,000+ `Text` nodes, 500,000+ `MENTIONS` edges (estimated)

**Acceptance Criteria:**
- [ ] 100,000+ nodes imported into Neo4j with verified counts
- [ ] Referential integrity check passes: zero orphaned edges (all `CITES` and `COMMENTARY_ON` targets exist)
- [ ] Content hash verification passes: re-running ingestion on unchanged texts produces no new nodes
- [ ] Pipeline completes a full sync in <24 hours (Tanakh + selected commentaries)
- [ ] Incremental sync completes in <2 hours when no changes detected
- [ ] Validation quarantine contains <1% of total records
- [ ] All Celery workers process jobs without error for 48 hours

**Milestone Gate: Data Ingestion Review**
- Gate Date: End of Week 7
- Gate Criteria: 100K+ nodes loaded; integrity checks pass; pipeline stable
- Exit Action: Proceed to Phase 4 or fix pipeline reliability

---

### Phase 4: Knowledge Extraction (Weeks 8–10)

**Goal**: AI-powered entity and relationship extraction is operational. Review queue UI is functional. Precision and recall meet minimum thresholds.

**Deliverables:**
1. Entity extraction agent:
   - Prompt templates for all 8 entity types (Person, Place, Concept, Mitzvah, Event, Text, Object, TimePeriod)
   - Few-shot examples with Hebrew context, stored in versioned YAML
   - JSON output schema with confidence scores
2. Relationship extraction agent:
   - Prompt templates for all 12 relationship types
   - Context chunking strategy with hierarchical two-pass approach
   - JSON output schema with evidence quotes
3. Confidence scoring system:
   - Score range 0.0–1.0 with calibrated thresholds
   - Calibration pipeline using human-validated subset (2,000 samples)
   - Score persistence in extraction records
4. Review queue UI:
   - Single-item review interface with source text, extraction, explanation, and accept/reject/edit buttons
   - Queue filters by entity type, confidence, source category, model version
   - Keyboard shortcuts for fast review
5. Bulk validation interface:
   - Grid view for batch review (10–50 items)
   - Bulk accept/reject actions
   - Auto-accept rules configuration
6. Validation metrics tracking:
   - Precision, recall, F1 per entity type and relationship type
   - Weekly calibration accuracy reports

**Acceptance Criteria:**
- [ ] Entity extraction precision >80% on human-annotated validation set
- [ ] Entity extraction recall >60% on human-annotated validation set
- [ ] Relationship extraction precision >75% on validation set
- [ ] Relationship extraction recall >55% on validation set
- [ ] Review queue UI loads in <2 seconds; item navigation is <500ms
- [ ] Calibrated confidence scores correlate with actual accuracy (correlation >0.7)
- [ ] 1,000+ extractions reviewed by human validators to establish baseline

**Milestone Gate: AI Extraction Review**
- Gate Date: End of Week 10
- Gate Criteria: Precision/recall thresholds met; review queue functional; calibration stable
- Exit Action: Proceed to Phase 5 or retrain/tune extraction prompts

---

### Phase 5: Graph Visualization (Weeks 11–13)

**Goal**: Interactive graph visualization layer is complete. All 5 primary graph views are functional and performant.

**Deliverables:**
1. Five graph views:
   - **Text Network View**: Texts connected by citation and commentary relationships
   - **People Network View**: Persons connected by teacher-student, authorship, and familial relationships
   - **Concept Map View**: Concepts connected by thematic and logical relationships
   - **Geographic View**: Places on an interactive map with event and person associations
   - **Timeline View**: Events and texts arranged chronologically with entity participation
2. Node detail panel:
   - Click any node to see: properties, connected nodes (paginated), source text snippets, author info
   - Inline editing for human reviewers (add/remove edges, correct properties)
3. Search interface:
   - Full-text search across Hebrew and English text
   - Entity search by name, type, era, category
   - Semantic search using Qdrant vector similarity
   - Search results rendered as a mini-graph (ego network of top result)
4. Performance optimizations:
   - Server-side graph sampling for large neighborhoods (>100 connected nodes)
   - Level-of-detail rendering (simplify labels at zoom-out)
   - WebWorker-based layout computation for graphs >500 nodes

**Acceptance Criteria:**
- [ ] All 5 graph views render without errors
- [ ] Graph renders 1,000 nodes at 60fps on a modern laptop (Chrome, 16GB RAM)
- [ ] Node detail panel loads in <1 second for nodes with <100 edges
- [ ] Full-text search returns results in <500ms for queries <5 words
- [ ] Semantic search returns top-10 results in <2 seconds
- [ ] Search results mini-graph renders in <1 second

**Milestone Gate: Visualization Review**
- Gate Date: End of Week 13
- Gate Criteria: All views functional; performance targets met; UX review passed
- Exit Action: Proceed to Phase 6 or optimize rendering performance

---

### Phase 6: AI Relationship Discovery (Weeks 14–16)

**Goal**: Automated relationship discovery is deployed at scale. Confidence scoring and human validation workflows produce high-quality graph edges.

**Deliverables:**
1. Automated relationship discovery:
   - Batch processing pipeline running on all text segments in the graph
   - Parallel extraction limited to 50 concurrent LLM calls with token-bucket rate limiting
   - Retry logic with dead-letter queue for failed extractions
2. Confidence scoring at scale:
   - Calibrated scores applied to all extractions
   - Auto-accept queue (≥0.90) feeding directly into Neo4j
   - Human review queues (0.70–0.89 and 0.50–0.69) populated and staffed
3. Human validation workflow:
   - Dispute mechanism for reviewer disagreements
   - Senior reviewer adjudication queue
   - Feedback loop from disputes to prompt calibration
4. Graph quality metrics:
   - Daily report: new edges, accepted edges, rejected edges, pending review
   - Weekly accuracy audit on random sample of auto-accepted edges
   - Monthly model performance report (precision/recall by model version)
5. Target graph enrichment:
   - 10,000+ AI-extracted relationships with confidence ≥0.80
   - Coverage across all major categories (Tanakh, Talmud, Halakhah)

**Acceptance Criteria:**
- [ ] 10,000+ AI-extracted relationships exist in Neo4j with confidence ≥0.80
- [ ] Auto-accept queue processes ≥500 edges/day without human intervention
- [ ] Human review queue depth does not exceed 2 weeks of backlog at current staffing
- [ ] Weekly spot-check of 100 auto-accepted edges shows >90% accuracy
- [ ] Dispute resolution time is <72 hours average
- [ ] Batch pipeline processes 10,000 text segments/day without failure

**Milestone Gate: AI Discovery Review**
- Gate Date: End of Week 16
- Gate Criteria: 10K+ high-confidence edges; pipeline stable; quality metrics green
- Exit Action: Proceed to Phase 7 or scale back extraction targets

---

### Phase 7: Advanced Torah Intelligence (Weeks 17–20)

**Goal**: Advanced analytical layers, graph layers, and API stabilization. Platform is production-ready.

**Deliverables:**
1. Graph layers (thematic overlays):
   - **Promises Layer**: Track divine promises, their recipients, and fulfillments across texts
   - **Segulot Layer**: Map protective practices, associated texts, and historical attestations
   - **Halakhic Chains Layer**: Trace halakhic rulings from source (Torah/Mishnah) through Talmud, Rishonim, and Acharonim
   - **Messianic Prophecies Layer**: Link prophecies to interpretations across commentaries
   - **Ethical Principles Layer**: Connect ethical concepts (truth, kindness, justice) across the corpus
   - **Mystical Concepts Layer**: Map Kabbalistic concepts (Sefirot, Partzufim) with textual sources
   - **Historical Events Layer**: Chronicle events with participants, locations, and source texts
2. Advanced search:
   - Cross-reference search: "Find all texts that discuss [concept] and [concept] together"
   - Pathfinding: Shortest path between two entities in the graph
   - Temporal search: "Find all events between [year] and [year]"
   - Geospatial search: "Find all events near [location]"
3. API stabilization:
   - REST API versioned at `/v1/` with OpenAPI spec
   - GraphQL endpoint for flexible client queries
   - Rate limiting: 100 req/min per API key (free tier), 10K req/min (premium tier)
   - API documentation with interactive playground (Swagger UI)
4. Production hardening:
   - Kubernetes deployment manifests
   - Terraform IaC for cloud infrastructure (AWS/GCP)
   - Load testing: API sustains 1,000 concurrent users with <200ms p95 latency
   - Backup strategy: Daily Neo4j dump, continuous PostgreSQL WAL archiving, Qdrant snapshot every 6 hours
5. Documentation:
   - API reference (`docs/API.md`)
   - User guide (`docs/USER_GUIDE.md`)
   - Admin guide (`docs/ADMIN_GUIDE.md`)
   - Architecture decision records (`docs/adr/`)

**Acceptance Criteria:**
- [ ] All 7 graph layers render correctly and can be toggled independently
- [ ] Pathfinding returns results in <3 seconds for paths of length ≤5
- [ ] API load tests pass: 1,000 concurrent users, p95 latency <200ms, error rate <0.1%
- [ ] OpenAPI spec is valid and Swagger UI renders all endpoints
- [ ] Backup recovery test succeeds: restore from backup in <4 hours
- [ ] All documentation is complete and reviewed
- [ ] Security scan passes (OWASP Top 10, no critical vulnerabilities)

**Milestone Gate: Production Readiness Review**
- Gate Date: End of Week 20
- Gate Criteria: All acceptance criteria pass; load tests green; security scan clean; documentation complete
- Exit Action: Declare production launch or schedule remediation sprint

---

## 4. Critical Path Dependencies

The following dependencies form the critical path. Delays in any of these tasks will cascade to subsequent phases.

```
Week 1-2:  [Architecture] ──▶ [Docker Compose] ──▶ [CI/CD]
                │
Week 3-4:   [Data Model] ──▶ [Neo4j Schema] ──▶ [PostgreSQL Schema] ──▶ [Qdrant Collections]
                │
Week 5-7:   [Import Pipeline] ──▶ [Sefaria API] ──▶ [Sefaria Export] ──▶ [100K Nodes]
                │
Week 8-10:  [Knowledge Extraction] ──▶ [Entity Agent] ──▶ [Relation Agent] ──▶ [Review Queue]
                │
Week 11-13: [Visualization] ──▶ [Graph Views] ──▶ [Search] ──▶ [Performance]
                │
Week 14-16: [AI Discovery] ──▶ [Batch Pipeline] ──▶ [10K Edges] ──▶ [Validation Workflow]
                │
Week 17-20: [Advanced Intelligence] ──▶ [Graph Layers] ──▶ [API Stabilization] ──▶ [Production]
```

**Key Dependency Chains:**
1. **Data Model → Import Pipeline**: Neo4j schema must be stable before bulk loading begins.
2. **Import Pipeline → Knowledge Extraction**: AI extraction requires text segments to be in the database.
3. **Knowledge Extraction → Visualization**: Graph views need populated nodes and edges to be meaningful.
4. **Visualization → AI Discovery**: Review queue UI (built in Phase 4/5) is required for Phase 6 validation.
5. **AI Discovery → Advanced Intelligence**: Graph layers require a dense graph to produce insightful overlays.

**Parallel Workstreams (Non-Critical Path):**
- Open Torah dataset adapters (can be developed in parallel with Sefaria ingestion)
- Frontend UI framework and component library (can be developed in parallel with backend)
- Documentation (continuously updated, not blocking)
- Infrastructure Terraform modules (can be developed in parallel with application code)

---

## 5. Milestone Gates with Acceptance Criteria

| Gate | Date | Criteria | Decision |
|------|------|----------|----------|
| **Architecture Review** | End of Week 2 | All services start; health checks pass; CI green; new dev onboarding <30 min | Proceed / Halt |
| **Data Model Review** | End of Week 4 | Schema tests pass; sample data round-trips; constraints active | Proceed / Fix |
| **Data Ingestion Review** | End of Week 7 | 100K+ nodes; zero orphaned edges; pipeline stable 48h; <1% quarantine | Proceed / Fix |
| **AI Extraction Review** | End of Week 10 | Precision >80%; recall >60%; review queue functional; calibration stable | Proceed / Retrain |
| **Visualization Review** | End of Week 13 | All 5 views functional; 1K nodes at 60fps; search <500ms | Proceed / Optimize |
| **AI Discovery Review** | End of Week 16 | 10K+ edges ≥0.80 confidence; pipeline stable; spot-check >90% | Proceed / Scale back |
| **Production Readiness** | End of Week 20 | All layers functional; API load tests pass; security clean; docs complete | Launch / Remediate |

**Gate Process:**
1. One week before the gate date, the engineering lead sends a readiness checklist to the review board (tech lead + domain expert + product owner).
2. Review board has 3 business days to evaluate.
3. Gate meeting: 1-hour review of acceptance criteria, demo, and Q&A.
4. Decision: `PROCEED` (all criteria met), `CONDITIONAL_PROCEED` (minor issues with documented remediation plan), or `HALT` (blocker requiring rework).

---

## 6. Risk Mitigation Strategies

| Risk | Probability | Impact | Mitigation Strategy | Owner |
|------|-------------|--------|----------------------|-------|
| **Sefaria API changes or rate limit reduction** | Medium | High | Abstract API calls behind adapter interface; maintain export ingestion as fallback; monitor Sefaria changelog | ETL Lead |
| **LLM API cost exceeds budget** | Medium | High | Implement aggressive caching of extraction results; use Haiku for low-complexity tasks; cap daily token budget with alerts | AI Lead |
| **Hebrew/Aramaic extraction accuracy is poor** | Medium | High | Invest in Hebrew-specific few-shot examples; fine-tune embeddings on Jewish texts; hire Hebrew-speaking reviewers | AI Lead |
| **Neo4j performance degrades at scale** | Medium | High | Implement graph partitioning by category; use read replicas for queries; pre-compute high-degree node neighborhoods | Backend Lead |
| **Domain expert reviewers are unavailable** | High | Medium | Build review queue with async workflow; train junior reviewers; implement bulk validation rules to reduce per-item review time | Product Lead |
| **Data quality issues block graph growth** | Medium | High | Automated validation pipeline catches 99% of errors before load; quarantine system prevents bad data propagation; weekly data quality audits | ETL Lead |
| **Scope creep in advanced layers** | High | Medium | Lock Phase 7 scope at Phase 5 gate; require ADR (Architecture Decision Record) for any scope change; de-scope lower-priority layers if needed | Tech Lead |
| **Team turnover or key person dependency** | Low | High | Document all decisions in ADRs; pair programming for critical components; maintain runbooks for all pipelines | Engineering Manager |
| **Open source license incompatibility** | Low | High | Legal review of all dataset licenses before ingestion; maintain license registry; exclude restrictive-license datasets | Product Lead |
| **Security breach of API or database** | Low | Critical | OWASP scan in CI; dependency vulnerability scanning; least-privilege access; encrypted at rest and in transit; annual pen test | Security Lead |

**Contingency Reserves:**
- **Time**: Each phase includes a 0.5-week buffer (except Phase 3 which has 3 weeks for 2 weeks of work = 1 week buffer).
- **Budget**: 20% LLM API cost contingency fund.
- **Staffing**: Maintain a backlog of "good first issues" to onboard new contributors quickly if team grows.

---

## 7. Resource Plan

### Team Composition

| Role | Count | Start Phase | Responsibility |
|------|-------|-------------|----------------|
| Tech Lead / Principal Engineer | 1 | 1 | Architecture, code review, critical path ownership |
| Backend Engineer (ETL) | 1 | 1 | Ingestion pipelines, data transformation, Neo4j |
| Backend Engineer (API) | 1 | 2 | FastAPI, GraphQL, database schema |
| AI Engineer | 1 | 4 | LLM prompts, extraction agents, calibration |
| Frontend Engineer | 1 | 5 | React, D3.js, graph visualization |
| DevOps / Infrastructure Engineer | 1 | 1 | Docker, K8s, Terraform, monitoring |
| Domain Expert (Rabbinic Scholar) | 1 | 4 | Review queue validation, dispute resolution, accuracy audits |
| Product Owner | 1 | 1 | Roadmap, requirements, stakeholder communication |

**Note**: The AI Engineer starts in Phase 4 but participates in design reviews during Phases 1–3. The Domain Expert starts in Phase 4 for review queue validation.

---

## 8. Communication Plan

| Cadence | Audience | Format | Content |
|---------|----------|--------|---------|
| Daily | Engineering team | Slack standup | Blockers, progress, pair programming needs |
| Weekly | Tech Lead + Engineers | 30-min sync | Phase progress, criteria status, risk review |
| Bi-weekly | Full team + stakeholders | Demo + retro | Working demo of completed features, retrospective |
| Phase Gate | Review board | 1-hour review | Acceptance criteria check, demo, go/no-go decision |
| Monthly | All stakeholders | Written report | Metrics, roadmap adjustments, budget review |

---

## 9. Metrics Dashboard

A live metrics dashboard tracks progress against the roadmap.

**Key Metrics:**
| Metric | Target | Measurement |
|--------|--------|-------------|
| Nodes in graph | 100K by Week 7, 500K by Week 20 | Neo4j `MATCH (n) RETURN count(n)` |
| Edges in graph | 500K by Week 7, 2M by Week 20 | Neo4j `MATCH ()-[r]-() RETURN count(r)` |
| AI-extracted edges | 10K by Week 16, 50K by Week 20 | `extraction_provenance` table count |
| Extraction precision | >80% | Weekly human validation sample |
| Extraction recall | >60% | Weekly human validation sample |
| Review queue depth | <2 weeks backlog | `review_queue` pending count |
| API p95 latency | <200ms | Prometheus histogram |
| Uptime | >99.9% | Monitoring dashboard |

---

*Document Version: 1.0*
*Last Updated: 2026-06-04*
*Maintainer: Torah Knowledge Graph Product Team*
