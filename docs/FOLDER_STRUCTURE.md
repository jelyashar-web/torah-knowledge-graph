# Torah Knowledge Graph — Folder Structure

## Root Layout

```
torah-knowledge-graph/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml              # Root orchestration (dev)
├── docker-compose.prod.yml         # Production overrides
├── Makefile                        # Common commands
│
├── docs/                           # Design & architecture docs
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── NEO4J_SCHEMA.md
│   ├── API_SPECIFICATION.md
│   ├── POSTGRESQL_SCHEMA.md
│   ├── QDRANT_SCHEMA.md
│   ├── ETL_DESIGN.md
│   ├── AI_EXTRACTION_DESIGN.md
│   ├── UI_DESIGN.md
│   ├── FOLDER_STRUCTURE.md
│   ├── IMPLEMENTATION_ROADMAP.md
│   └── decisions/                 # ADRs (Architecture Decision Records)
│       ├── 001-triple-database.md
│       ├── 002-neo4j-community.md
│       └── 003-react-flow-d3.md
│
├── frontend/                       # Next.js 15 application
│   ├── Dockerfile
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── .env.local.example
│   │
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   │   ├── layout.tsx          # Root layout with providers
│   │   │   ├── page.tsx            # Home / default graph view
│   │   │   ├── globals.css
│   │   │   │
│   │   │   ├── graph/
│   │   │   │   ├── page.tsx        # Main graph explorer
│   │   │   │   └── [view]/         # /graph/local, /graph/topic, etc.
│   │   │   │       ├── page.tsx
│   │   │   │       └── layout.tsx
│   │   │   │
│   │   │   ├── search/
│   │   │   │   └── page.tsx        # Advanced search interface
│   │   │   │
│   │   │   ├── node/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx    # Node detail page (SEO-friendly)
│   │   │   │
│   │   │   ├── layers/
│   │   │   │   └── page.tsx        # Graph layer selector
│   │   │   │
│   │   │   ├── validation/
│   │   │   │   └── page.tsx        # Human validation queue
│   │   │   │
│   │   │   └── api/                # Next.js API routes (proxies)
│   │   │       └── [...path]/
│   │   │           └── route.ts
│   │   │
│   │   ├── components/
│   │   │   ├── graph/
│   │   │   │   ├── GraphCanvas.tsx
│   │   │   │   ├── GraphNode.tsx
│   │   │   │   ├── GraphEdge.tsx
│   │   │   │   ├── GraphControls.tsx
│   │   │   │   ├── MiniMap.tsx
│   │   │   │   ├── LayoutEngine.ts
│   │   │   │   └── layers/
│   │   │   │       ├── LayerRenderer.tsx
│   │   │   │       └── LayerFilter.tsx
│   │   │   │
│   │   │   ├── ui/                 # shadcn/ui components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── tabs.tsx
│   │   │   │   ├── slider.tsx
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── search/
│   │   │   │   ├── GlobalSearch.tsx
│   │   │   │   ├── SearchResults.tsx
│   │   │   │   ├── FacetFilter.tsx
│   │   │   │   └── SearchSuggestion.tsx
│   │   │   │
│   │   │   ├── panels/
│   │   │   │   ├── NodeDetailPanel.tsx
│   │   │   │   ├── SourcesTab.tsx
│   │   │   │   ├── ConnectionsTab.tsx
│   │   │   │   ├── CitationsTab.tsx
│   │   │   │   └── RelatedTab.tsx
│   │   │   │
│   │   │   ├── navigation/
│   │   │   │   ├── TopNavigation.tsx
│   │   │   │   ├── LayerSelector.tsx
│   │   │   │   ├── ViewSelector.tsx
│   │   │   │   └── BottomBar.tsx
│   │   │   │
│   │   │   └── shared/
│   │   │       ├── HebrewText.tsx
│   │   │       ├── ProvenanceBadge.tsx
│   │   │       ├── ConfidenceIndicator.tsx
│   │   │       ├── LoadingState.tsx
│   │   │       └── ErrorBoundary.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useGraphStore.ts    # Zustand store
│   │   │   ├── useNodeQuery.ts     # React Query hooks
│   │   │   ├── useSearchQuery.ts
│   │   │   ├── useGraphLayout.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── useKeyboardShortcuts.ts
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts              # API client (axios/fetch)
│   │   │   ├── neo4j-client.ts   # Neo4j browser-compatible client
│   │   │   ├── qdrant-client.ts
│   │   │   ├── websocket.ts
│   │   │   ├── colors.ts           # Node/layer color definitions
│   │   │   ├── typography.ts
│   │   │   ├── constants.ts
│   │   │   └── utils.ts
│   │   │
│   │   ├── types/
│   │   │   ├── nodes.ts            # TypeScript node type definitions
│   │   │   ├── relationships.ts
│   │   │   ├── api.ts
│   │   │   ├── graph.ts
│   │   │   └── search.ts
│   │   │
│   │   └── styles/
│   │       ├── hebrew-fonts.css
│   │       └── graph-themes.css
│   │
│   ├── public/
│   │   ├── fonts/
│   │   │   ├── SBLHebrew.woff2
│   │   │   └── FrankRuehl.woff2
│   │   ├── icons/
│   │   └── favicon.ico
│   │
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── e2e/
│           └── graph-navigation.spec.ts
│
├── backend/                        # FastAPI application
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .env.example
│   ├── alembic.ini
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app factory
│   │   ├── config.py               # Pydantic Settings
│   │   ├── dependencies.py         # FastAPI dependencies
│   │   ├── celery.py               # Celery app factory
│   │   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # /auth/* endpoints
│   │   │   ├── graph.py            # /graph/* endpoints
│   │   │   ├── nodes.py            # /nodes/* endpoints
│   │   │   ├── relationships.py    # /relationships/* endpoints
│   │   │   ├── search.py           # /search/* endpoints
│   │   │   ├── layers.py           # /layers/* endpoints
│   │   │   ├── ingestion.py        # /ingestion/* endpoints
│   │   │   ├── extraction.py       # /extraction/* endpoints
│   │   │   ├── visualization.py    # /visualization/* endpoints
│   │   │   └── websocket.py        # WebSocket handlers
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── neo4j/              # Neo4j node/rel models
│   │   │   │   ├── nodes.py
│   │   │   │   ├── relationships.py
│   │   │   │   └── queries.py
│   │   │   │
│   │   │   ├── postgres/           # SQLAlchemy ORM models
│   │   │   │   ├── user.py
│   │   │   │   ├── source.py
│   │   │   │   ├── text.py
│   │   │   │   ├── extraction_job.py
│   │   │   │   ├── audit_log.py
│   │   │   │   ├── ai_inference.py
│   │   │   │   ├── confidence.py
│   │   │   │   └── api_log.py
│   │   │   │
│   │   │   └── pydantic/           # Pydantic request/response schemas
│   │   │       ├── auth.py
│   │   │       ├── graph.py
│   │   │       ├── nodes.py
│   │   │       ├── relationships.py
│   │   │       ├── search.py
│   │   │       ├── extraction.py
│   │   │       └── ingestion.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── neo4j_service.py    # Graph CRUD operations
│   │   │   ├── search_service.py   # Full-text + vector search
│   │   │   ├── auth_service.py     # JWT + RBAC
│   │   │   ├── node_service.py     # Node business logic
│   │   │   ├── relationship_service.py
│   │   │   ├── visualization_service.py
│   │   │   └── layer_service.py    # Graph layer filtering
│   │   │
│   │   ├── workers/
│   │   │   ├── __init__.py
│   │   │   ├── etl_worker.py       # Celery tasks for ETL
│   │   │   ├── extraction_worker.py  # AI extraction tasks
│   │   │   ├── embedding_worker.py   # Vector embedding generation
│   │   │   └── analytics_worker.py   # Graph analytics (GDS)
│   │   │
│   │   ├── clients/
│   │   │   ├── __init__.py
│   │   │   ├── neo4j_client.py     # Neo4j driver wrapper
│   │   │   ├── postgres_client.py  # Async SQLAlchemy session
│   │   │   ├── qdrant_client.py    # Qdrant HTTP client
│   │   │   ├── redis_client.py     # Redis connection
│   │   │   ├── sefaria_client.py   # Sefaria API client
│   │   │   ├── anthropic_client.py # Anthropic API client
│   │   │   └── openai_client.py    # OpenAI API client
│   │   │
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth_middleware.py
│   │   │   ├── rate_limit.py
│   │   │   ├── logging.py
│   │   │   └── error_handler.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validators.py
│   │       ├── hebrew_utils.py     # Hebrew text processing
│   │       ├── reference_parser.py # "Genesis 1:1" → structured
│   │       ├── gematria.py         # Gematria calculations
│   │       └── logger.py
│   │
│   ├── alembic/
│   │   ├── env.py
│   │   ├── versions/
│   │   └── script.py.mako
│   │
│   ├── scripts/
│   │   ├── deploy_neo4j_schema.py
│   │   ├── create_qdrant_collections.py
│   │   ├── seed_data.py
│   │   └── health_check.py
│   │
│   └── tests/
│       ├── conftest.py
│       ├── unit/
│       ├── integration/
│       └── fixtures/
│
├── shared/                         # Shared types and contracts
│   ├── types/
│   │   ├── nodes.ts                # TypeScript node types
│   │   ├── relationships.ts
│   │   └── api.ts
│   ├── contracts/
│   │   └── openapi.yaml            # Single source OpenAPI spec
│   └── constants/
│       ├── node_types.ts
│       ├── relationship_types.ts
│       └── corpora.ts
│
├── databases/                      # Database schemas and migrations
│   ├── neo4j/
│   │   ├── constraints.cypher
│   │   ├── indexes.cypher
│   │   ├── schema.cypher
│   │   └── seed/
│   │       ├── books.cypher
│   │       └── sefirot.cypher
│   │
│   ├── postgres/
│   │   ├── migrations/
│   │   │   ├── 001_initial.sql
│   │   │   └── 002_add_audit_log.sql
│   │   └── init/
│   │       └── 01_create_extensions.sql
│   │
│   └── qdrant/
│       ├── collections.yaml
│       └── init.py
│
├── etl/                            # ETL pipelines
│   ├── pipelines/
│   │   ├── __init__.py
│   │   ├── sefaria_api.py
│   │   ├── sefaria_export.py
│   │   └── open_datasets.py
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── sefaria_adapter.py
│   │   ├── tei_adapter.py
│   │   └── plain_text_adapter.py
│   ├── transforms/
│   │   ├── __init__.py
│   │   ├── hebrew_normalizer.py
│   │   ├── reference_parser.py
│   │   └── text_segmenter.py
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── neo4j_loader.py
│   │   ├── postgres_loader.py
│   │   └── qdrant_loader.py
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── schema_validator.py
│   │   ├── integrity_checker.py
│   │   └── duplicate_detector.py
│   └── tests/
│       └── fixtures/
│
├── ai-extraction/                  # AI extraction service
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── entity_agent.py         # Entity extraction LLM agent
│   │   ├── relationship_agent.py   # Relationship extraction agent
│   │   └── citation_agent.py       # Source citation extraction
│   ├── prompts/
│   │   ├── entity_extraction/
│   │   │   ├── person.j2
│   │   │   ├── place.j2
│   │   │   ├── concept.j2
│   │   │   └── mitzvah.j2
│   │   ├── relationship_extraction/
│   │   │   ├── commentary_on.j2
│   │   │   ├── mentions.j2
│   │   │   ├── related_to.j2
│   │   │   └── alludes_to.j2
│   │   └── explanation/
│   │       └── relationship_justification.j2
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── json_parser.py
│   │   └── citation_parser.py
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── confidence_calibrator.py
│   │   └── source_validator.py
│   └── tests/
│       └── fixtures/
│
├── infrastructure/                 # Docker, K8s, IaC
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   ├── frontend.Dockerfile
│   │   └── worker.Dockerfile
│   ├── k8s/
│   │   ├── namespace.yaml
│   │   ├── neo4j/
│   │   ├── postgres/
│   │   ├── qdrant/
│   │   ├── backend/
│   │   ├── frontend/
│   │   ├── worker/
│   │   ├── ingress.yaml
│   │   └── configmaps/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── monitoring/
│       ├── prometheus/
│       └── grafana/
│           └── dashboards/
│
└── scripts/                        # Utility scripts
    ├── setup.sh                    # Initial project setup
    ├── dev-start.sh                # Start dev environment
    ├── dev-stop.sh                 # Stop dev environment
    ├── db-reset.sh                 # Reset all databases
    ├── backup.sh                   # Backup databases
    └── health-check.sh             # Full system health check
```

## Naming Conventions

### Files
- Components: PascalCase (`GraphCanvas.tsx`)
- Hooks: camelCase with `use` prefix (`useGraphStore.ts`)
- Utilities: camelCase (`hebrewUtils.ts`)
- Styles: kebab-case (`graph-themes.css`)
- Config: kebab-case (`tailwind.config.ts`)
- Python modules: snake_case (`neo4j_client.py`)
- SQL migrations: `NNN_description.sql`

### Git Branches
- `main` — Production-ready
- `develop` — Integration branch
- `feature/xxx` — Features
- `bugfix/xxx` — Bug fixes
- `hotfix/xxx` — Production hotfixes

## Environment Variables

```bash
# .env.example
# Neo4j
NEO4J_USER=neo4j
NEO4J_PASSWORD=torah-graph-secure
NEO4J_URI=bolt://localhost:7687

# PostgreSQL
POSTGRES_USER=tkg
POSTGRES_PASSWORD=tkg-postgres-secure
POSTGRES_DB=torah_knowledge_graph
DATABASE_URL=postgresql+asyncpg://tkg:tkg-postgres-secure@localhost:5432/torah_knowledge_graph

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis
REDIS_URL=redis://localhost:6379/0

# Auth
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256

# AI APIs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/v1/ws
```
