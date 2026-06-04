# Torah Knowledge Graph — Docker Architecture

## Overview

This document defines the complete Docker Compose architecture for local development and production deployment of the Torah Knowledge Graph platform. All services are containerized with health checks, resource limits, restart policies, and explicit dependency ordering.

---

## `docker-compose.yml`

```yaml
# =============================================================================
# Torah Knowledge Graph — Docker Compose
# Version: 3.8
# =============================================================================
services:
  # ===========================================================================
  # Neo4j — Graph Database
  # ===========================================================================
  neo4j:
    image: neo4j:5-community
    container_name: tkgraph-neo4j
    restart: unless-stopped
    ports:
      - "7474:7474"   # HTTP (Browser)
      - "7687:7687"   # Bolt
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_plugins:/plugins
      - ./init/neo4j/apoc.conf:/conf/apoc.conf:ro
    environment:
      - NEO4J_AUTH=${NEO4J_AUTH:-neo4j/changeme}
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
      - NEO4J_apoc_export_file_enabled=true
      - NEO4J_apoc_import_file_enabled=true
      - NEO4J_apoc_trigger_enabled=true
      - NEO4J_dbms_memory_heap_initial__size=${NEO4J_HEAP_INIT:-512m}
      - NEO4J_dbms_memory_heap_max__size=${NEO4J_HEAP_MAX:-2G}
    healthcheck:
      test: ["CMD", "wget", "-q", "-O", "-", "http://localhost:7474"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - tkgraph-backend
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  # ===========================================================================
  # PostgreSQL 16 — Relational Database
  # ===========================================================================
  postgres:
    image: postgres:16-alpine
    container_name: tkgraph-postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init/postgres:/docker-entrypoint-initdb.d:ro
      - ./init/postgres/scripts:/scripts:ro
    environment:
      - POSTGRES_USER=${POSTGRES_USER:-tkgraph_app}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-changeme}
      - POSTGRES_DB=${POSTGRES_DB:-torah_knowledge}
      - PGDATA=/var/lib/postgresql/data/pgdata
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 10s
    networks:
      - tkgraph-backend
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

  # ===========================================================================
  # Qdrant — Vector Database
  # ===========================================================================
  qdrant:
    image: qdrant/qdrant:latest
    container_name: tkgraph-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"     # REST API
      - "6334:6334"     # gRPC
    volumes:
      - qdrant_data:/qdrant/storage
      - ./init/qdrant:/qdrant/init:ro
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__STORAGE__STORAGE_PATH=/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s
    networks:
      - tkgraph-backend
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 1G

  # ===========================================================================
  # Redis — Celery Broker & Cache
  # ===========================================================================
  redis:
    image: redis:7-alpine
    container_name: tkgraph-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 5s
    networks:
      - tkgraph-backend
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

  # ===========================================================================
  # Backend — FastAPI
  # ===========================================================================
  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
      args:
        - APP_ENV=${APP_ENV:-development}
    container_name: tkgraph-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=${APP_ENV:-development}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=${NEO4J_USER:-neo4j}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD:-changeme}
      - QDRANT_URL=http://qdrant:6333
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
      - JWT_SECRET=${JWT_SECRET:-changeme-immediately}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 15s
      timeout: 5s
      retries: 5
      start_period: 30s
    depends_on:
      postgres:
        condition: service_healthy
      neo4j:
        condition: service_healthy
      qdrant:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - tkgraph-backend
      - tkgraph-frontend
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M

  # ===========================================================================
  # Celery Worker — Background Task Processor
  # ===========================================================================
  celery_worker:
    build:
      context: ../backend
      dockerfile: Dockerfile.worker
    container_name: tkgraph-celery-worker
    restart: unless-stopped
    environment:
      - APP_ENV=${APP_ENV:-development}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=${NEO4J_USER:-neo4j}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD:-changeme}
      - QDRANT_URL=http://qdrant:6333
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    command: celery -A app.celery worker -l info -c 4 -Q extraction,default --beat
    depends_on:
      postgres:
        condition: service_healthy
      neo4j:
        condition: service_healthy
      qdrant:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - tkgraph-backend
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 1G

  # ===========================================================================
  # Celery Beat — Periodic Task Scheduler
  # ===========================================================================
  celery_beat:
    build:
      context: ../backend
      dockerfile: Dockerfile.worker
    container_name: tkgraph-celery-beat
    restart: unless-stopped
    environment:
      - APP_ENV=${APP_ENV:-development}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=${NEO4J_USER:-neo4j}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD:-changeme}
      - QDRANT_URL=http://qdrant:6333
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    command: celery -A app.celery beat -l info --scheduler redisbeat.RedisScheduler
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - tkgraph-backend
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 128M
        reservations:
          cpus: '0.1'
          memory: 64M

  # ===========================================================================
  # Frontend — Next.js
  # ===========================================================================
  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
      args:
        - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}
        - NEXT_PUBLIC_APP_NAME=${NEXT_PUBLIC_APP_NAME:-Torah Knowledge Graph}
    container_name: tkgraph-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=${NODE_ENV:-production}
      - API_URL=http://backend:8000
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}
    healthcheck:
      test: ["CMD", "wget", "-q", "-O", "-", "http://localhost:3000/api/health"]
      interval: 15s
      timeout: 5s
      retries: 5
      start_period: 30s
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - tkgraph-frontend
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

# =============================================================================
# Volumes
# =============================================================================
volumes:
  neo4j_data:
    driver: local
  neo4j_logs:
    driver: local
  neo4j_import:
    driver: local
  neo4j_plugins:
    driver: local
  postgres_data:
    driver: local
  qdrant_data:
    driver: local
  redis_data:
    driver: local

# =============================================================================
# Networks
# =============================================================================
networks:
  tkgraph-backend:
    driver: bridge
    internal: false
  tkgraph-frontend:
    driver: bridge
    internal: false
```

---

## Service Reference

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `neo4j` | `neo4j:5-community` | 7474, 7687 | Graph database (entities & relationships) |
| `postgres` | `postgres:16-alpine` | 5432 | Relational data, audit logs, users |
| `qdrant` | `qdrant/qdrant:latest` | 6333, 6334 | Vector search (semantic retrieval) |
| `redis` | `redis:7-alpine` | 6379 | Celery broker + result backend + cache |
| `backend` | FastAPI (built) | 8000 | REST API, auth, orchestration |
| `celery_worker` | FastAPI worker (built) | — | Background extraction & sync tasks |
| `celery_beat` | FastAPI worker (built) | — | Periodic task scheduler |
| `frontend` | Next.js (built) | 3000 | Web UI |

---

## Environment Variables

### Required (no defaults safe for production)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEO4J_AUTH` | Neo4j username/password | `neo4j/StrongPassword123` |
| `POSTGRES_PASSWORD` | PostgreSQL application password | `StrongPassword123` |
| `JWT_SECRET` | HS256 secret for JWT signing | `32-byte-random-string` |

### Optional (sensible defaults provided)

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Runtime environment (`development`, `staging`, `production`) |
| `POSTGRES_USER` | `tkgraph_app` | PostgreSQL role name |
| `POSTGRES_DB` | `torah_knowledge` | Database name |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `changeme` | Neo4j password |
| `NEO4J_HEAP_INIT` | `512m` | Initial JVM heap |
| `NEO4J_HEAP_MAX` | `2G` | Maximum JVM heap |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Frontend → Backend API URL |
| `NEXT_PUBLIC_APP_NAME` | `Torah Knowledge Graph` | Branding string |
| `NODE_ENV` | `production` | Node.js runtime mode |

### `.env` Template

```bash
# .env (never commit to git)
APP_ENV=development

# PostgreSQL
POSTGRES_USER=tkgraph_app
POSTGRES_PASSWORD=changeme-immediately
POSTGRES_DB=torah_knowledge

# Neo4j
NEO4J_AUTH=neo4j/changeme-immediately
NEO4J_HEAP_INIT=512m
NEO4J_HEAP_MAX=2G

# JWT
JWT_SECRET=replace-with-32-byte-random-string

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Torah Knowledge Graph
NODE_ENV=production

# Observability
LOG_LEVEL=INFO
```

---

## Initialization Scripts

### PostgreSQL Init (`init/postgres/01_schema.sql`)

Place `POSTGRESQL_SCHEMA.md` DDL in `init/postgres/01_schema.sql`. PostgreSQL executes all `*.sql` files in `docker-entrypoint-initdb.d` on first container start.

### Qdrant Init (`init/qdrant/init.sh`)

```bash
#!/bin/sh
# init/qdrant/init.sh
# Qdrant runs this after the REST API is available.

QDRANT_URL="http://localhost:6333"

until curl -sf "${QDRANT_URL}/healthz" > /dev/null; do
  echo "Waiting for Qdrant..."
  sleep 2
done

curl -X PUT "${QDRANT_URL}/collections/torah_texts" \
  -H "Content-Type: application/json" \
  -d '{"vectors":{"size":768,"distance":"Cosine","on_disk":true}}'

curl -X PUT "${QDRANT_URL}/collections/torah_entities" \
  -H "Content-Type: application/json" \
  -d '{"vectors":{"size":768,"distance":"Cosine","on_disk":true}}'

echo "Qdrant collections initialized."
```

### Neo4j Init (`init/neo4j/apoc.conf`)

```properties
# APOC configuration
apoc.export.file.enabled=true
apoc.import.file.enabled=true
apoc.trigger.enabled=true
```

---

## Health Checks

All stateful services expose health checks. The backend depends on all databases being healthy before it starts.

```
backend  -->  postgres (healthy)
        -->  neo4j   (healthy)
        -->  qdrant  (healthy)
        -->  redis   (healthy)

frontend -->  backend (healthy)
```

---

## Production Considerations

### Resource Limits

The `deploy.resources` blocks in the compose file define production-grade limits. On Docker Swarm or Kubernetes, these translate directly to container limits. For plain Docker Compose, they are advisory but respected by Docker Desktop and Linux daemon.

### Restart Policies

- `unless-stopped`: Services restart on crash or host reboot, but respect explicit `docker compose stop`.
- For production orchestrators (Swarm/K8s), replace with `restart: always` or pod restart policies.

### Security

1. **Secrets**: Never commit `.env`. Use Docker Secrets (Swarm) or Kubernetes Secrets in production.
2. **Network Isolation**: `tkgraph-backend` and `tkgraph-frontend` separate internal traffic from external. Only `backend` and `frontend` expose external ports.
3. **Non-root Images**: Use Alpine-based images where possible. The FastAPI backend should run as a non-root user in its Dockerfile.
4. **Database Exposure**: PostgreSQL and Neo4j ports are mapped to localhost for local dev. In production, remove port mappings and access via internal network only.

### Scaling

| Service | Scale Strategy | Notes |
|---------|---------------|-------|
| `backend` | Horizontal (replicas) | Stateless; place behind reverse proxy |
| `celery_worker` | Horizontal (replicas) | Increase `-c` concurrency or spawn more workers |
| `postgres` | Vertical (bigger instance) | Or read replicas for reporting |
| `neo4j` | Vertical (bigger instance) | Neo4j Enterprise for causal clustering |
| `qdrant` | Horizontal (distributed) | Qdrant Enterprise or self-hosted cluster |
| `redis` | Sentinel/Cluster | For HA beyond single container |

### Reverse Proxy / SSL

In production, place `traefik` or `nginx` in front of `frontend` and `backend`:

```yaml
  traefik:
    image: traefik:v3.0
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - tkgraph-frontend
```

### Monitoring Hooks

- **Prometheus**: Scrape `backend:8000/metrics`, `qdrant:6333/metrics`.
- **Grafana**: Dashboard for API latency, Qdrant search latency, Neo4j query times.
- **Alertmanager**: Alert on `healthcheck` failures, disk usage > 80%.

### Backup Strategy

| Service | Method | Frequency | Retention |
|---------|--------|-----------|-----------|
| PostgreSQL | `pg_dump` | Daily | 7 days |
| Neo4j | `neo4j-admin dump` | Daily | 7 days |
| Qdrant | Snapshot API | Daily | 7 days |
| Redis | RDB + AOF | Continuous | N/A (ephemeral cache) |

---

## Quick Start

```bash
# 1. Clone and enter infrastructure directory
cd /home/vix/Projects/torah-knowledge-graph/infrastructure

# 2. Copy and edit environment
cp .env.example .env
# Edit .env — change all passwords and secrets

# 3. Start all services
docker compose up -d

# 4. Verify health
docker compose ps
docker compose logs -f backend

# 5. Access
# Neo4j Browser: http://localhost:7474
# Qdrant UI:    http://localhost:6333/dashboard
# API Docs:     http://localhost:8000/docs
# Frontend:     http://localhost:3000
```
