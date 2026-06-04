# Torah Knowledge Graph — PostgreSQL Schema

## Overview

This document defines the complete PostgreSQL 16 schema for the Torah Knowledge Graph platform. The relational layer stores users, content sources, raw texts, extraction jobs, audit trails, AI inference metadata, confidence scoring, and API request logging.

All tables use `gen_random_uuid()` (PostgreSQL 16+) for primary keys. JSONB is used extensively for flexible metadata. GIN indexes are placed on JSONB columns to support fast containment and key lookups.

---

## DDL — Schema Setup

```sql
-- =============================================================================
-- Torah Knowledge Graph — PostgreSQL Schema
-- Version: 1.0.0
-- PostgreSQL: 16+
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- 1. USERS
-- =============================================================================
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'reader',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    preferences     JSONB NOT NULL DEFAULT '{}',

    CONSTRAINT users_email_unique UNIQUE (email),
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_role_check CHECK (role IN ('admin', 'editor', 'reader', 'api'))
);

COMMENT ON TABLE users IS 'Platform users with RBAC roles';
COMMENT ON COLUMN users.preferences IS 'JSONB: ui_language, notifications_enabled, default_search_mode, etc.';

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_preferences_gin ON users USING GIN (preferences);

-- =============================================================================
-- 2. SOURCES
-- =============================================================================
CREATE TABLE sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           TEXT NOT NULL,
    hebrew_title    TEXT,
    url             TEXT,
    download_date   TIMESTAMPTZ NOT NULL DEFAULT now(),
    checksum        TEXT NOT NULL,
    format          TEXT NOT NULL DEFAULT 'pdf',
    metadata        JSONB NOT NULL DEFAULT '{}',

    CONSTRAINT sources_url_unique UNIQUE (url),
    CONSTRAINT sources_checksum_unique UNIQUE (checksum),
    CONSTRAINT sources_format_check CHECK (format IN ('pdf', 'txt', 'html', 'docx', 'xml', 'json'))
);

COMMENT ON TABLE sources IS 'Original Torah text sources (books, articles, archives)';
COMMENT ON COLUMN sources.metadata IS 'JSONB: author, publisher, publication_year, language, tags, category';

CREATE INDEX idx_sources_title ON sources USING gin(to_tsvector('english', title));
CREATE INDEX idx_sources_hebrew_title ON sources USING gin(to_tsvector('simple', hebrew_title));
CREATE INDEX idx_sources_format ON sources(format);
CREATE INDEX idx_sources_download_date ON sources(download_date);
CREATE INDEX idx_sources_metadata_gin ON sources USING GIN (metadata);

-- =============================================================================
-- 3. TEXTS
-- =============================================================================
CREATE TABLE texts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id   UUID NOT NULL,
    content     TEXT NOT NULL,
    format      TEXT NOT NULL DEFAULT 'plain',
    language    TEXT NOT NULL DEFAULT 'he',
    parsed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata    JSONB NOT NULL DEFAULT '{}',

    CONSTRAINT texts_source_id_fk FOREIGN KEY (source_id)
        REFERENCES sources(id) ON DELETE CASCADE,
    CONSTRAINT texts_format_check CHECK (format IN ('plain', 'markdown', 'html', 'structured')),
    CONSTRAINT texts_language_check CHECK (language IN ('he', 'en', 'ar', 'yi', 'la'))
);

COMMENT ON TABLE texts IS 'Parsed/extracted text content from sources';
COMMENT ON COLUMN texts.metadata IS 'JSONB: chapter, section, page_number, paragraph_index, word_count';

CREATE INDEX idx_texts_source_id ON texts(source_id);
CREATE INDEX idx_texts_language ON texts(language);
CREATE INDEX idx_texts_parsed_at ON texts(parsed_at);
CREATE INDEX idx_texts_content_fts ON texts USING gin(to_tsvector('simple', content));
CREATE INDEX idx_texts_metadata_gin ON texts USING GIN (metadata);

-- =============================================================================
-- 4. EXTRACTION_JOBS
-- =============================================================================
CREATE TABLE extraction_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type        TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending',
    payload         JSONB NOT NULL DEFAULT '{}',
    result          JSONB,
    error_log       TEXT,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_by      UUID NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT extraction_jobs_created_by_fk FOREIGN KEY (created_by)
        REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT extraction_jobs_job_type_check CHECK (
        job_type IN ('entity_extraction', 'relationship_extraction', 'summarization', 'translation', 'classification')
    ),
    CONSTRAINT extraction_jobs_status_check CHECK (
        status IN ('pending', 'running', 'paused', 'completed', 'failed', 'cancelled')
    ),
    CONSTRAINT extraction_jobs_completed_after_started CHECK (
        completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at
    )
);

COMMENT ON TABLE extraction_jobs IS 'AI/ML extraction job queue and history';
COMMENT ON COLUMN extraction_jobs.payload IS 'JSONB: source_id, text_ids, model_params, priority';
COMMENT ON COLUMN extraction_jobs.result IS 'JSONB: extracted_entities[], extracted_relationships[], summary';

CREATE INDEX idx_extraction_jobs_status ON extraction_jobs(status);
CREATE INDEX idx_extraction_jobs_job_type ON extraction_jobs(job_type);
CREATE INDEX idx_extraction_jobs_created_by ON extraction_jobs(created_by);
CREATE INDEX idx_extraction_jobs_created_at ON extraction_jobs(created_at);
CREATE INDEX idx_extraction_jobs_started_at ON extraction_jobs(started_at);
CREATE INDEX idx_extraction_jobs_payload_gin ON extraction_jobs USING GIN (payload);
CREATE INDEX idx_extraction_jobs_result_gin ON extraction_jobs USING GIN (result);

-- =============================================================================
-- 5. RELATIONSHIPS_AUDIT_LOG
-- =============================================================================
CREATE TABLE relationships_audit_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action              TEXT NOT NULL,
    relationship_type   TEXT NOT NULL,
    from_node           TEXT NOT NULL,
    to_node             TEXT NOT NULL,
    old_state           JSONB,
    new_state           JSONB,
    actor_id            UUID,
    timestamp           TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT relationships_audit_log_actor_id_fk FOREIGN KEY (actor_id)
        REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT relationships_audit_log_action_check CHECK (
        action IN ('created', 'updated', 'deleted', 'merged', 'validated', 'rejected')
    )
);

COMMENT ON TABLE relationships_audit_log IS 'Immutable audit trail for all graph relationship mutations';
COMMENT ON COLUMN relationships_audit_log.old_state IS 'JSONB: previous relationship properties';
COMMENT ON COLUMN relationships_audit_log.new_state IS 'JSONB: new relationship properties';

CREATE INDEX idx_relationships_audit_log_timestamp ON relationships_audit_log(timestamp);
CREATE INDEX idx_relationships_audit_log_action ON relationships_audit_log(action);
CREATE INDEX idx_relationships_audit_log_relationship_type ON relationships_audit_log(relationship_type);
CREATE INDEX idx_relationships_audit_log_from_node ON relationships_audit_log(from_node);
CREATE INDEX idx_relationships_audit_log_to_node ON relationships_audit_log(to_node);
CREATE INDEX idx_relationships_audit_log_actor_id ON relationships_audit_log(actor_id);
CREATE INDEX idx_relationships_audit_log_old_state_gin ON relationships_audit_log USING GIN (old_state);
CREATE INDEX idx_relationships_audit_log_new_state_gin ON relationships_audit_log USING GIN (new_state);

-- =============================================================================
-- 6. AI_INFERENCE_METADATA
-- =============================================================================
CREATE TABLE ai_inference_metadata (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id          UUID NOT NULL,
    model           TEXT NOT NULL,
    prompt_version  TEXT NOT NULL,
    prompt_hash     TEXT NOT NULL,
    temperature     NUMERIC(3, 2) NOT NULL DEFAULT 0.0,
    raw_response    TEXT,
    tokens_used     INTEGER NOT NULL DEFAULT 0,
    latency_ms      INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ai_inference_metadata_job_id_fk FOREIGN KEY (job_id)
        REFERENCES extraction_jobs(id) ON DELETE CASCADE,
    CONSTRAINT ai_inference_metadata_temperature_check CHECK (
        temperature >= 0.0 AND temperature <= 2.0
    ),
    CONSTRAINT ai_inference_metadata_tokens_used_check CHECK (tokens_used >= 0),
    CONSTRAINT ai_inference_metadata_latency_ms_check CHECK (latency_ms >= 0)
);

COMMENT ON TABLE ai_inference_metadata IS 'Lineage and observability for every AI inference call';
COMMENT ON COLUMN ai_inference_metadata.prompt_hash IS 'SHA-256 of the rendered prompt for reproducibility';

CREATE INDEX idx_ai_inference_metadata_job_id ON ai_inference_metadata(job_id);
CREATE INDEX idx_ai_inference_metadata_model ON ai_inference_metadata(model);
CREATE INDEX idx_ai_inference_metadata_prompt_version ON ai_inference_metadata(prompt_version);
CREATE INDEX idx_ai_inference_metadata_created_at ON ai_inference_metadata(created_at);
CREATE INDEX idx_ai_inference_metadata_tokens_used ON ai_inference_metadata(tokens_used);

-- =============================================================================
-- 7. CONFIDENCE_SCORES
-- =============================================================================
CREATE TABLE confidence_scores (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    relationship_id       TEXT NOT NULL, -- references Neo4j relationship UUID
    score               NUMERIC(4, 3) NOT NULL,
    method              TEXT NOT NULL DEFAULT 'model',
    model_version       TEXT,
    human_validated     BOOLEAN NOT NULL DEFAULT FALSE,
    validated_by        UUID,
    validated_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT confidence_scores_validated_by_fk FOREIGN KEY (validated_by)
        REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT confidence_scores_score_check CHECK (score >= 0.0 AND score <= 1.0),
    CONSTRAINT confidence_scores_method_check CHECK (
        method IN ('model', 'human', 'ensemble', 'rule_based', 'hybrid')
    ),
    CONSTRAINT confidence_scores_validated_consistency CHECK (
        (human_validated = FALSE AND validated_by IS NULL AND validated_at IS NULL)
        OR
        (human_validated = TRUE AND validated_by IS NOT NULL AND validated_at IS NOT NULL)
    )
);

COMMENT ON TABLE confidence_scores IS 'Trust scoring for graph relationships bridging AI and human validation';

CREATE INDEX idx_confidence_scores_relationship_id ON confidence_scores(relationship_id);
CREATE INDEX idx_confidence_scores_score ON confidence_scores(score);
CREATE INDEX idx_confidence_scores_method ON confidence_scores(method);
CREATE INDEX idx_confidence_scores_human_validated ON confidence_scores(human_validated);
CREATE INDEX idx_confidence_scores_validated_by ON confidence_scores(validated_by);
CREATE INDEX idx_confidence_scores_created_at ON confidence_scores(created_at);

-- =============================================================================
-- 8. API_REQUEST_LOG
-- =============================================================================
CREATE TABLE api_request_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint            TEXT NOT NULL,
    method              TEXT NOT NULL,
    duration_ms         INTEGER NOT NULL,
    status_code         INTEGER NOT NULL,
    user_id             UUID,
    ip_address          INET,
    request_body_hash   TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT api_request_log_user_id_fk FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT api_request_log_method_check CHECK (
        method IN ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS')
    ),
    CONSTRAINT api_request_log_duration_ms_check CHECK (duration_ms >= 0),
    CONSTRAINT api_request_log_status_code_check CHECK (status_code BETWEEN 100 AND 599)
);

COMMENT ON TABLE api_request_log IS 'API observability and rate-limiting audit trail';
COMMENT ON COLUMN api_request_log.request_body_hash IS 'SHA-256 of request body for deduplication/replay analysis';

CREATE INDEX idx_api_request_log_created_at ON api_request_log(created_at);
CREATE INDEX idx_api_request_log_endpoint ON api_request_log(endpoint);
CREATE INDEX idx_api_request_log_method ON api_request_log(method);
CREATE INDEX idx_api_request_log_status_code ON api_request_log(status_code);
CREATE INDEX idx_api_request_log_user_id ON api_request_log(user_id);
CREATE INDEX idx_api_request_log_ip_address ON api_request_log(ip_address);
CREATE INDEX idx_api_request_log_duration_ms ON api_request_log(duration_ms);

-- =============================================================================
-- ROW-LEVEL SECURITY (RLS) — Foundation
-- =============================================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE texts ENABLE ROW LEVEL SECURITY;
ALTER TABLE extraction_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE relationships_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_inference_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE confidence_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_request_log ENABLE ROW LEVEL SECURITY;

-- Admin sees everything
CREATE POLICY admin_all ON users FOR ALL TO admin USING (true) WITH CHECK (true);

-- Users see only their own rows (template; application must set role via SET ROLE)
CREATE POLICY users_self ON users FOR SELECT USING (id = current_setting('app.current_user_id')::UUID);

-- =============================================================================
-- AUTO-UPDATE updated_at TRIGGER
-- =============================================================================
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp_users
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_timestamp();

-- =============================================================================
-- PARTITIONING SETUP (api_request_log — optional, for high-volume production)
-- =============================================================================
-- Uncomment for production partitioning by month:
-- CREATE TABLE api_request_log_partitioned (LIKE api_request_log INCLUDING ALL)
--   PARTITION BY RANGE (created_at);
-- CREATE TABLE api_request_log_2024_01 PARTITION OF api_request_log_partitioned
--   FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- =============================================================================
-- INITIAL DATA
-- =============================================================================
INSERT INTO users (email, hashed_password, role, preferences)
VALUES (
    'admin@torah-knowledge.local',
    -- bcrypt hash of 'changeme-immediately' (cost=12)
    '$2a$12$K0ByB.6YI2/OYrB4fQOYLe6QdRg6XnYlYqYqYqYqYqYqYqYqYqYqYq',
    'admin',
    '{"ui_language": "en", "notifications_enabled": true, "default_search_mode": "semantic"}'
);

-- =============================================================================
-- GRANTS
-- =============================================================================
-- Create a dedicated application role (run as superuser):
-- CREATE ROLE tkgraph_app WITH LOGIN PASSWORD 'strong_password';
-- GRANT CONNECT ON DATABASE torah_knowledge TO tkgraph_app;
-- GRANT USAGE ON SCHEMA public TO tkgraph_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO tkgraph_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO tkgraph_app;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO tkgraph_app;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO tkgraph_app;
```

---

## Entity Relationship Diagram

```text
users ||--o{ extraction_jobs        : creates
users ||--o{ relationships_audit_log : acts
users ||--o{ confidence_scores      : validates
users ||--o{ api_request_log        : requests

sources ||--o{ texts                : contains

extraction_jobs ||--o{ ai_inference_metadata : produces
texts ||--o{ extraction_jobs         : input
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| `UUID` primary keys | Prevents enumeration attacks; simplifies distributed ingestion |
| `JSONB` metadata columns | Torah sources vary wildly in metadata fields; rigid columns would require constant migrations |
| GIN indexes on JSONB | Enables fast containment queries (`@>`, `?`, `?&`) for metadata filtering |
| `NUMERIC(4,3)` for confidence | Three decimal places (0.000–1.000) is sufficient granularity |
| `INET` for IP address | PostgreSQL native type supports CIDR queries for range analysis |
| `TIMESTAMPTZ` everywhere | Eliminates ambiguity; store UTC, convert at application layer |
| Separate `ai_inference_metadata` table | Decouples observability from job state; enables post-hoc analysis without touching job records |
| `relationship_id` as `TEXT` | References Neo4j relationship UUIDs; Neo4j relationships lack native UUIDs, so we assign them in the application |
| RLS foundation | Policies are minimal but present; enforcement relies on `app.current_user_id` being set by the application layer |

---

## Migration Path

1. Run the DDL above against a fresh PostgreSQL 16 instance.
2. Apply the dedicated role and grants block (bottom of DDL).
3. Verify with `\dt` and check all indexes with `\di`.
4. Load initial admin user and rotate the password immediately.
