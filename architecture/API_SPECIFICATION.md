# Torah Knowledge Graph — REST API Specification

## 1. Overview

This document defines the complete REST API for the Torah Knowledge Graph platform. The API follows OpenAPI 3.1 conventions and uses JSON for all request and response bodies.

### 1.1 Base URL

```
Production:  https://api.torah-knowledge-graph.example.com/api/v1
Development: http://localhost:8000/api/v1
```

### 1.2 Authentication

All endpoints except `/auth/login`, `/auth/register`, and `/auth/refresh` require a valid JWT access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### 1.3 Standard Response Envelope

Every response uses a consistent envelope:

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-06-04T12:00:00Z"
  }
}
```

### 1.4 Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      { "field": "name", "message": "Field required" }
    ]
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-06-04T12:00:00Z"
  }
}
```

### 1.5 Pagination

List endpoints use cursor-based pagination:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page_size` | integer | 20 | Items per page (max 100) |
| `cursor` | string | — | Opaque cursor from previous response |

**Paginated Response Meta:**

```json
{
  "meta": {
    "pagination": {
      "page_size": 20,
      "next_cursor": "eyJpZCI6...",
      "has_more": true,
      "total_count": 1542
    }
  }
}
```

### 1.6 Rate Limiting Headers

All responses include rate-limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1717509600
```

### 1.7 HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `204` | No Content (successful DELETE) |
| `400` | Bad Request (validation error) |
| `401` | Unauthorized (missing/invalid token) |
| `403` | Forbidden (insufficient role) |
| `404` | Not Found |
| `409` | Conflict (duplicate, e.g., unique constraint violation) |
| `422` | Unprocessable Entity (semantic error) |
| `429` | Too Many Requests (rate limited) |
| `500` | Internal Server Error |

---

## 2. Authentication Endpoints

### 2.1 POST /auth/register
Register a new user account.

**Request Schema:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "Reuven Cohen",
  "role": "reader"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `email` | string | Yes | Valid email, max 255 chars |
| `password` | string | Yes | Min 12 chars, 1 uppercase, 1 lowercase, 1 digit |
| `name` | string | Yes | Max 100 chars |
| `role` | string | No | Default `reader`. Allowed: `reader`, `contributor` |

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": "usr-123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "name": "Reuven Cohen",
    "role": "reader",
    "created_at": "2026-06-04T12:00:00Z"
  },
  "meta": { ... }
}
```

---

### 2.2 POST /auth/login
Authenticate and receive access/refresh tokens.

**Request Schema:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 900,
    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2g...",
    "user": {
      "id": "usr-123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "name": "Reuven Cohen",
      "role": "reader"
    }
  },
  "meta": { ... }
}
```

**Cookies Set:**
- `refresh_token` — httpOnly, Secure, SameSite=Strict, Max-Age=604800

---

### 2.3 POST /auth/refresh
Obtain a new access token using a refresh token.

**Request:**
- Cookie: `refresh_token=<token>`
- Or body: `{ "refresh_token": "..." }`

**Response 200:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 900
  },
  "meta": { ... }
}
```

---

### 2.4 POST /auth/logout
Revoke the current session. Blacklists the refresh token.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response 204:**
No body. Clears `refresh_token` cookie.

---

## 3. Graph Query Endpoints

### 3.1 POST /graph/query
Execute a parameterized Cypher query against Neo4j. Restricted to read-only operations.

**Request Schema:**
```json
{
  "query": "MATCH (v:Verse {book: $book}) RETURN v LIMIT $limit",
  "parameters": {
    "book": "Genesis",
    "limit": 10
  }
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `query` | string | Yes | Read-only Cypher. Blocked: `CREATE`, `DELETE`, `SET`, `REMOVE`, `MERGE`, `DROP` |
| `parameters` | object | No | Key-value map for parameterized substitution |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "columns": ["v"],
    "records": [
      {
        "v": {
          "id": "verse-gen-1-1",
          "book": "Genesis",
          "chapter_number": 1,
          "verse_number": 1,
          "hebrew_text": "בראשית ברא אלהים את השמים ואת הארץ"
        }
      }
    ],
    "stats": {
      "rows_returned": 1,
      "query_time_ms": 12
    }
  },
  "meta": { ... }
}
```

---

### 3.2 POST /graph/query/advanced
Execute a pre-defined advanced query template with parameters.

**Request Schema:**
```json
{
  "template": "path_between_nodes",
  "parameters": {
    "start_id": "concept-free-will",
    "end_id": "concept-divine-providence",
    "max_hops": 6
  }
}
```

**Available Templates:**
| Template | Description | Required Params |
|----------|-------------|-----------------|
| `path_between_nodes` | Shortest path | `start_id`, `end_id`, `max_hops` |
| `neighborhood` | N-hop neighborhood | `node_id`, `depth`, `relationship_types` |
| `common_neighbors` | Shared connections | `node_a_id`, `node_b_id` |
| `centrality` | Degree centrality for label | `label`, `limit` |
| `gematria_matches` | Nodes matching gematria | `value`, `label` |

---

## 4. Node CRUD Endpoints

All node CRUD endpoints follow the pattern `POST/GET/PUT/DELETE /api/nodes/{type}`.

### 4.1 POST /nodes/{type}
Create a new node of the given type.

**URL Parameter:**
- `type` — One of: `verse`, `chapter`, `book`, `person`, `tzaddik`, `mitzvah`, `concept`, `sefirah`, `divinename`, `prayer`, `promise`, `segulah`, `tikkun`, `place`, `historicalevent`, `halachictopic`

**Request Example (type=verse):**
```json
{
  "book": "Genesis",
  "chapter_number": 1,
  "verse_number": 2,
  "hebrew_text": "והארץ היתה תהו ובהו...",
  "english_text": "And the earth was without form...",
  "source_citation": "Tanakh"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": "verse-gen-1-2",
    "type": "Verse",
    "properties": { ... },
    "created_at": "2026-06-04T12:00:00Z",
    "status": "pending"
  },
  "meta": { ... }
}
```

**Permissions:** `contributor`, `validator`, `admin`. Readers get `403`.

---

### 4.2 GET /nodes/{type}
List nodes of the given type with filtering.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Full-text search query |
| `status` | string | Filter by `public`, `pending`, `rejected` |
| `created_by` | string | Filter by creator user ID |
| `sort` | string | Sort field (default: `created_at`) |
| `order` | string | `asc` or `desc` (default: `desc`) |
| `page_size` | integer | Pagination size |
| `cursor` | string | Pagination cursor |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "verse-gen-1-1",
        "type": "Verse",
        "properties": { ... }
      }
    ],
    "pagination": {
      "page_size": 20,
      "next_cursor": "eyJpZCI6...",
      "has_more": true,
      "total_count": 23145
    }
  },
  "meta": { ... }
}
```

---

### 4.3 GET /nodes/{type}/{id}
Retrieve a single node by ID.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "verse-gen-1-1",
    "type": "Verse",
    "properties": { ... },
    "relationship_counts": {
      "COMMENTARY_ON": 47,
      "MENTIONS": 12,
      "RELATED_TO": 8
    },
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-06-01T00:00:00Z",
    "status": "public"
  },
  "meta": { ... }
}
```

---

### 4.4 PUT /nodes/{type}/{id}
Full update of a node. All properties are replaced.

**Request Schema:** Same shape as POST, plus `id` must match URL.

**Permissions:** Owner (contributor) or `validator` / `admin`.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "verse-gen-1-1",
    "type": "Verse",
    "properties": { ... },
    "updated_at": "2026-06-04T12:05:00Z",
    "status": "pending"
  },
  "meta": { ... }
}
```

---

### 4.5 PATCH /nodes/{type}/{id}
Partial update of a node. Only provided fields are updated.

**Request Example:**
```json
{
  "english_text": "Updated translation...",
  "status": "pending"
}
```

**Response 200:** Same shape as PUT.

---

### 4.6 DELETE /nodes/{type}/{id}
Soft-delete a node (sets `status` to `rejected`). Hard delete only for `admin`.

**Query Parameters:**
- `hard` — boolean, default `false`. If `true`, permanently deletes the node and all relationships.

**Response 204** for soft delete.

**Response 200** for hard delete:
```json
{
  "success": true,
  "data": {
    "deleted": true,
    "relationships_removed": 47,
    "cascade_affected": [
      { "type": "Verse", "id": "verse-gen-1-1" }
    ]
  },
  "meta": { ... }
}
```

---

## 5. Relationship CRUD Endpoints

### 5.1 POST /relationships/{type}
Create a new relationship of the given type.

**URL Parameter:**
- `type` — One of: `commentary_on`, `quotes`, `mentions`, `related_to`, `alludes_to`, `gematria_match`, `notarikon`, `atbash`, `halacha_source`, `kabbalah_source`, `part_of`, `causes`, `repairs`, `promises`, `segulah_for`, `tikkun_for`, `opposite_of`, `derived_from`

**Request Example (type=commentary_on):**
```json
{
  "source_node_id": "concept-rashi-gen-1-1",
  "target_node_id": "verse-gen-1-1",
  "properties": {
    "commentary_type": "Rashi",
    "commentary_text": "For the sake of Torah and Israel...",
    "language": "hebrew",
    "source_citation": "Rashi on Genesis 1:1",
    "confidence": 1.0,
    "notes": "Classic commentary"
  }
}
```

| Field | Type | Required |
|-------|------|----------|
| `source_node_id` | string | Yes |
| `target_node_id` | string | Yes |
| `properties` | object | Yes (type-specific) |

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": "rel-001",
    "type": "COMMENTARY_ON",
    "source_node_id": "concept-rashi-gen-1-1",
    "target_node_id": "verse-gen-1-1",
    "properties": { ... },
    "created_at": "2026-06-04T12:00:00Z",
    "status": "pending"
  },
  "meta": { ... }
}
```

---

### 5.2 GET /relationships/{type}
List relationships of the given type with filtering.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `source_node_id` | string | Filter by source node |
| `target_node_id` | string | Filter by target node |
| `status` | string | Filter by status |
| `created_by` | string | Filter by creator |
| `page_size` | integer | Pagination size |
| `cursor` | string | Pagination cursor |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "relationships": [
      {
        "id": "rel-001",
        "type": "COMMENTARY_ON",
        "source_node_id": "concept-rashi-gen-1-1",
        "target_node_id": "verse-gen-1-1",
        "properties": { ... },
        "status": "public"
      }
    ],
    "pagination": { ... }
  },
  "meta": { ... }
}
```

---

### 5.3 GET /relationships/{type}/{id}
Retrieve a single relationship by ID.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "rel-001",
    "type": "COMMENTARY_ON",
    "source_node_id": "concept-rashi-gen-1-1",
    "target_node_id": "verse-gen-1-1",
    "properties": { ... },
    "created_at": "2026-01-01T00:00:00Z",
    "status": "public"
  },
  "meta": { ... }
}
```

---

### 5.4 PUT /relationships/{type}/{id}
Full update of a relationship's properties.

**Request Schema:** Same as POST, but `id` must match URL.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "rel-001",
    "type": "COMMENTARY_ON",
    "properties": { ... },
    "updated_at": "2026-06-04T12:10:00Z"
  },
  "meta": { ... }
}
```

---

### 5.5 DELETE /relationships/{type}/{id}
Delete a relationship.

**Response 204** (no body).

---

## 6. Search Endpoints

### 6.1 GET /search/fulltext
Full-text search across indexed node properties.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `labels` | string[] | No | Restrict to labels: `Verse`, `Book`, `Person`, etc. |
| `language` | string | No | `hebrew`, `english`, `both` (default: `both`) |
| `page_size` | integer | No | Default 20 |
| `cursor` | string | No | Pagination cursor |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "node": {
          "id": "verse-gen-1-1",
          "type": "Verse",
          "properties": { ... }
        },
        "highlights": {
          "hebrew_text": ["בראשית <em>ברא</em> אלהים"],
          "english_text": ["In the <em>beginning</em> God created"]
        },
        "score": 0.92
      }
    ],
    "pagination": { ... }
  },
  "meta": { ... }
}
```

---

### 6.2 POST /search/vector
Semantic vector search using Qdrant.

**Request Schema:**
```json
{
  "query_text": "creation of the world",
  "labels": ["Verse", "Concept"],
  "limit": 20,
  "min_score": 0.7
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query_text` | string | Yes | Text to embed and search |
| `labels` | string[] | No | Filter by node labels |
| `limit` | integer | No | Default 20, max 100 |
| `min_score` | float | No | Minimum cosine similarity (0.0–1.0) |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "node": {
          "id": "concept-creation",
          "type": "Concept",
          "properties": { ... }
        },
        "score": 0.89,
        "vector_id": "vec-123"
      }
    ],
    "query_embedding_model": "text-embedding-3-large"
  },
  "meta": { ... }
}
```

---

### 6.3 POST /search/hybrid
Hybrid search combining full-text and vector results with RRF (Reciprocal Rank Fusion).

**Request Schema:**
```json
{
  "query_text": "light and darkness",
  "labels": ["Verse", "Concept", "Sefirah"],
  "limit": 20,
  "fts_weight": 0.4,
  "vector_weight": 0.6
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query_text` | string | Yes | Query for both FTS and vector |
| `labels` | string[] | No | Filter by node labels |
| `limit` | integer | No | Default 20 |
| `fts_weight` | float | No | Weight for full-text score (0.0–1.0) |
| `vector_weight` | float | No | Weight for vector score (0.0–1.0) |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "node": { ... },
        "rrf_score": 0.95,
        "fts_score": 0.88,
        "vector_score": 0.91
      }
    ],
    "fusion_method": "RRF",
    "k": 60
  },
  "meta": { ... }
}
```

---

## 7. Visualization Data Endpoints

### 7.1 POST /visualization/neighborhood
Return a node's local neighborhood for graph rendering.

**Request Schema:**
```json
{
  "node_id": "sefirah-chesed",
  "depth": 2,
  "relationship_types": ["RELATED_TO", "OPPOSITE_OF", "PART_OF"],
  "limit_per_hop": 50,
  "include_properties": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `node_id` | string | Yes | Center node ID |
| `depth` | integer | No | 1 or 2 (default: 1) |
| `relationship_types` | string[] | No | Filter relationship types |
| `limit_per_hop` | integer | No | Max nodes per hop (default: 50) |
| `include_properties` | boolean | No | Include full node properties (default: false) |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "center": { "id": "sefirah-chesed", "type": "Sefirah", "name": "Chesed" },
    "nodes": [
      { "id": "sefirah-chesed", "type": "Sefirah", "name": "Chesed", "x": 0, "y": 0 },
      { "id": "sefirah-gevurah", "type": "Sefirah", "name": "Gevurah", "x": 100, "y": 0 },
      { "id": "sefirah-tiferet", "type": "Sefirah", "name": "Tiferet", "x": 50, "y": 86 }
    ],
    "edges": [
      { "id": "rel-101", "type": "OPPOSITE_OF", "source": "sefirah-chesed", "target": "sefirah-gevurah" },
      { "id": "rel-102", "type": "RELATED_TO", "source": "sefirah-chesed", "target": "sefirah-tiferet" }
    ],
    "layout": "force-directed",
    "stats": { "node_count": 11, "edge_count": 14 }
  },
  "meta": { ... }
}
```

---

### 7.2 POST /visualization/path
Return the shortest path between two nodes for graph rendering.

**Request Schema:**
```json
{
  "start_id": "verse-gen-1-1",
  "end_id": "concept-creation",
  "max_hops": 6,
  "relationship_types": ["COMMENTARY_ON", "RELATED_TO", "DERIVED_FROM"]
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "nodes": [
      { "id": "verse-gen-1-1", "type": "Verse", "name": "Genesis 1:1" },
      { "id": "concept-creation", "type": "Concept", "name": "Creation" }
    ],
    "edges": [
      { "id": "rel-201", "type": "COMMENTARY_ON", "source": "concept-creation", "target": "verse-gen-1-1" }
    ],
    "hops": 1,
    "alternate_paths": 3
  },
  "meta": { ... }
}
```

---

### 7.3 POST /visualization/subgraph
Return a custom subgraph based on a Cypher-like query specification.

**Request Schema:**
```json
{
  "query": {
    "start_nodes": [{ "label": "Sefirah", "property": "world", "value": "Atzilut" }],
    "traversal": {
      "depth": 2,
      "relationship_types": ["PART_OF", "RELATED_TO", "OPPOSITE_OF"],
      "direction": "both"
    }
  },
  "layout": "hierarchical",
  "layout_options": {
    "rankdir": "TB",
    "nodesep": 80,
    "ranksep": 120
  }
}
```

**Response 200:** Same shape as `/visualization/neighborhood`.

---

## 8. Ingestion Pipeline Endpoints

### 8.1 POST /ingestion/trigger
Trigger a new ingestion job.

**Request Schema:**
```json
{
  "source_type": "sefaria",
  "source_config": {
    "book": "Genesis",
    "chapters": [1, 2, 3]
  },
  "extract_entities": true,
  "extract_relationships": true,
  "generate_embeddings": true,
  "auto_approve": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_type` | string | Yes | `upload`, `sefaria`, `url`, `github` |
| `source_config` | object | Yes | Type-specific configuration |
| `extract_entities` | boolean | No | Run AI entity extraction (default: true) |
| `extract_relationships` | boolean | No | Run AI relationship extraction (default: true) |
| `generate_embeddings` | boolean | No | Generate Qdrant embeddings (default: true) |
| `auto_approve` | boolean | No | Skip review queue (admin only) |

**Response 202 (Accepted):**
```json
{
  "success": true,
  "data": {
    "job_id": "job-123e4567-e89b-12d3-a456-426614174000",
    "status": "queued",
    "queued_at": "2026-06-04T12:00:00Z",
    "estimated_completion": "2026-06-04T12:05:00Z",
    "celery_task_id": "task-abc123"
  },
  "meta": { ... }
}
```

---

### 8.2 GET /ingestion/{job_id}/status
Get the status of an ingestion job.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "job_id": "job-123e4567-e89b-12d3-a456-426614174000",
    "status": "running",
    "progress": {
      "total_chunks": 150,
      "processed_chunks": 73,
      "extracted_entities": 45,
      "extracted_relationships": 32,
      "failed_chunks": 0
    },
    "started_at": "2026-06-04T12:00:00Z",
    "updated_at": "2026-06-04T12:03:00Z",
    "completed_at": null,
    "error_message": null
  },
  "meta": { ... }
}
```

**Status Values:** `queued`, `running`, `completed`, `failed`, `cancelled`

---

### 8.3 POST /ingestion/{job_id}/cancel
Cancel a running ingestion job.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "job_id": "job-123e4567-e89b-12d3-a456-426614174000",
    "status": "cancelled",
    "cancelled_at": "2026-06-04T12:04:00Z",
    "rollback_status": "completed"
  },
  "meta": { ... }
}
```

---

### 8.4 GET /ingestion
List all ingestion jobs with filtering.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status |
| `source_type` | string | Filter by source type |
| `created_by` | string | Filter by creator |
| `page_size` | integer | Pagination size |
| `cursor` | string | Pagination cursor |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "jobs": [ ... ],
    "pagination": { ... }
  },
  "meta": { ... }
}
```

---

## 9. AI Extraction Job Endpoints

### 9.1 POST /ai-extraction/submit
Submit a new AI extraction job for entity and relationship extraction from raw text.

**Request Schema:**
```json
{
  "text": "ויאמר ה' אל משה...",
  "source_reference": "Exodus 3:1-15",
  "extraction_types": ["entities", "relationships", "gematria"],
  "model": "claude-sonnet-4-6",
  "confidence_threshold": 0.75,
  "language": "hebrew"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | Raw Hebrew or English text to analyze |
| `source_reference` | string | Yes | Canonical reference for the text |
| `extraction_types` | string[] | No | `entities`, `relationships`, `gematria`, `notarikon`, `atbash` |
| `model` | string | No | LLM model to use |
| `confidence_threshold` | float | No | Minimum confidence to include (default: 0.7) |
| `language` | string | No | `hebrew`, `english`, `aramaic` |

**Response 202:**
```json
{
  "success": true,
  "data": {
    "job_id": "ai-job-123e4567-e89b-12d3-a456-426614174000",
    "status": "queued",
    "estimated_tokens": 4500,
    "queued_at": "2026-06-04T12:00:00Z"
  },
  "meta": { ... }
}
```

---

### 9.2 GET /ai-extraction/{job_id}/status
Get the status of an AI extraction job.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "job_id": "ai-job-123e4567-e89b-12d3-a456-426614174000",
    "status": "completed",
    "progress": {
      "total_tokens": 4200,
      "prompt_tokens": 3800,
      "completion_tokens": 400
    },
    "started_at": "2026-06-04T12:00:00Z",
    "completed_at": "2026-06-04T12:01:30Z",
    "model_used": "claude-sonnet-4-6",
    "cost_usd": 0.012
  },
  "meta": { ... }
}
```

---

### 9.3 GET /ai-extraction/{job_id}/results
Retrieve the extracted results from a completed job.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "job_id": "ai-job-123e4567-e89b-12d3-a456-426614174000",
    "extracted_entities": [
      {
        "type": "Person",
        "name": "Moses",
        "name_hebrew": "משה",
        "confidence": 0.98,
        "span": { "start": 12, "end": 16 },
        "proposed_properties": {
          "role": "prophet",
          "biography": "Leader who spoke to God at the burning bush"
        }
      },
      {
        "type": "DivineName",
        "name": "YHVH",
        "name_hebrew": "יהוה",
        "confidence": 1.0,
        "span": { "start": 6, "end": 10 }
      }
    ],
    "extracted_relationships": [
      {
        "type": "MENTIONS",
        "source_node_type": "Verse",
        "source_reference": "Exodus 3:4",
        "target_node_type": "Person",
        "target_name": "Moses",
        "confidence": 0.99,
        "mention_context": "God called to him from the bush"
      }
    ],
    "gematria_findings": [
      {
        "word": "משה",
        "gematria_value": 345,
        "matches": ["השם"]
      }
    ]
  },
  "meta": { ... }
}
```

---

### 9.4 POST /ai-extraction/{job_id}/validate
Validate (approve or reject) AI extraction results. Only `validator` or `admin`.

**Request Schema:**
```json
{
  "action": "approve",
  "entity_approvals": [
    { "extracted_index": 0, "action": "approve", "node_id": "person-moses" },
    { "extracted_index": 1, "action": "reject", "reason": "Already exists as divinename-yhvh" }
  ],
  "relationship_approvals": [
    { "extracted_index": 0, "action": "approve", "relationship_id": "rel-301" }
  ],
  "bulk_action": null
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | Yes | `approve`, `reject`, `approve_all`, `reject_all` |
| `entity_approvals` | object[] | No | Per-entity validation decisions |
| `relationship_approvals` | object[] | No | Per-relationship validation decisions |
| `bulk_action` | string | No | Overrides per-item decisions if set |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "job_id": "ai-job-123e4567-e89b-12d3-a456-426614174000",
    "validation_summary": {
      "entities_approved": 1,
      "entities_rejected": 1,
      "relationships_approved": 1,
      "relationships_rejected": 0,
      "nodes_created": 1,
      "relationships_created": 1
    },
    "validated_at": "2026-06-04T12:10:00Z",
    "validated_by": "usr-validator-001"
  },
  "meta": { ... }
}
```

---

### 9.5 GET /ai-extraction
List all AI extraction jobs.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status |
| `model` | string | Filter by model used |
| `created_by` | string | Filter by submitter |
| `page_size` | integer | Pagination size |
| `cursor` | string | Pagination cursor |

**Response 200:** Paginated list of AI extraction job summaries.

---

## 10. Admin & System Endpoints

### 10.1 GET /admin/audit-log
Retrieve audit logs. Admin only.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entity_type` | string | Filter by entity type |
| `entity_id` | string | Filter by entity ID |
| `action` | string | `create`, `update`, `delete`, `validate` |
| `user_id` | string | Filter by actor |
| `from` | datetime | Start of time range |
| `to` | datetime | End of time range |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": "audit-001",
        "timestamp": "2026-06-04T12:00:00Z",
        "user_id": "usr-123",
        "action": "create",
        "entity_type": "Verse",
        "entity_id": "verse-gen-1-2",
        "diff": { "hebrew_text": "והארץ היתה תהו..." },
        "ip_address": "192.168.1.1"
      }
    ],
    "pagination": { ... }
  },
  "meta": { ... }
}
```

---

### 10.2 GET /health
System health check. No authentication required.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "neo4j": { "status": "up", "latency_ms": 5 },
      "postgresql": { "status": "up", "latency_ms": 2 },
      "qdrant": { "status": "up", "latency_ms": 8 },
      "redis": { "status": "up", "latency_ms": 1 },
      "celery": { "status": "up", "active_workers": 4 }
    },
    "version": "1.0.0",
    "uptime_seconds": 86400
  },
  "meta": { ... }
}
```

---

## 11. WebSocket Protocol

### 11.1 Connection
- **Endpoint:** `wss://api.torah-knowledge-graph.example.com/ws/graph/{session_id}`
- **Authentication:** JWT in `Authorization` header during handshake.

### 11.2 Client → Server Messages

```json
// Subscribe to a graph view
{
  "action": "subscribe",
  "view": "sefirot",
  "filters": { "status": "public" }
}

// Request layout update
{
  "action": "layout",
  "algorithm": "force-directed",
  "options": { "iterations": 100, "cooling_factor": 0.95 }
}

// Ping
{
  "action": "ping",
  "timestamp": 1717509600000
}
```

### 11.3 Server → Client Messages

```json
// Node created event
{
  "event": "node.created",
  "data": {
    "node": { "id": "verse-gen-1-2", "type": "Verse", ... },
    "timestamp": "2026-06-04T12:00:00Z"
  }
}

// Relationship created event
{
  "event": "relationship.created",
  "data": {
    "relationship": { "id": "rel-301", "type": "COMMENTARY_ON", ... },
    "timestamp": "2026-06-04T12:00:00Z"
  }
}

// Layout progress
{
  "event": "layout.progress",
  "data": {
    "iteration": 45,
    "total_iterations": 100,
    "energy": 0.023,
    "nodes_positioned": 120
  }
}

// Pong
{
  "event": "pong",
  "data": { "client_timestamp": 1717509600000, "server_timestamp": 1717509600012 }
}
```

---

## 12. Appendix A: Complete Endpoint Summary

| Method | Path | Auth | Role Min | Description |
|--------|------|------|----------|-------------|
| POST | /auth/register | No | — | Register new user |
| POST | /auth/login | No | — | Authenticate |
| POST | /auth/refresh | No | — | Refresh access token |
| POST | /auth/logout | Yes | reader | Logout |
| POST | /graph/query | Yes | reader | Cypher read query |
| POST | /graph/query/advanced | Yes | reader | Advanced query template |
| POST | /nodes/{type} | Yes | contributor | Create node |
| GET | /nodes/{type} | Yes | reader | List nodes |
| GET | /nodes/{type}/{id} | Yes | reader | Get node |
| PUT | /nodes/{type}/{id} | Yes | contributor | Full update node |
| PATCH | /nodes/{type}/{id} | Yes | contributor | Partial update node |
| DELETE | /nodes/{type}/{id} | Yes | contributor | Delete node |
| POST | /relationships/{type} | Yes | contributor | Create relationship |
| GET | /relationships/{type} | Yes | reader | List relationships |
| GET | /relationships/{type}/{id} | Yes | reader | Get relationship |
| PUT | /relationships/{type}/{id} | Yes | contributor | Update relationship |
| DELETE | /relationships/{type}/{id} | Yes | contributor | Delete relationship |
| GET | /search/fulltext | Yes | reader | Full-text search |
| POST | /search/vector | Yes | reader | Vector search |
| POST | /search/hybrid | Yes | reader | Hybrid search |
| POST | /visualization/neighborhood | Yes | reader | Neighborhood subgraph |
| POST | /visualization/path | Yes | reader | Path visualization |
| POST | /visualization/subgraph | Yes | reader | Custom subgraph |
| POST | /ingestion/trigger | Yes | admin | Trigger ingestion |
| GET | /ingestion | Yes | admin | List ingestion jobs |
| GET | /ingestion/{job_id}/status | Yes | admin | Ingestion status |
| POST | /ingestion/{job_id}/cancel | Yes | admin | Cancel ingestion |
| POST | /ai-extraction/submit | Yes | contributor | Submit AI extraction |
| GET | /ai-extraction | Yes | contributor | List AI jobs |
| GET | /ai-extraction/{job_id}/status | Yes | contributor | AI job status |
| GET | /ai-extraction/{job_id}/results | Yes | contributor | AI job results |
| POST | /ai-extraction/{job_id}/validate | Yes | validator | Validate AI results |
| GET | /admin/audit-log | Yes | admin | View audit logs |
| GET | /health | No | — | Health check |

---

## 13. Appendix B: Error Codes

| Code | HTTP | Description | Recovery |
|------|------|-------------|----------|
| `UNAUTHORIZED` | 401 | Missing or invalid token | Re-authenticate |
| `FORBIDDEN` | 403 | Insufficient role | Contact admin |
| `NODE_NOT_FOUND` | 404 | Node ID does not exist | Verify ID |
| `RELATIONSHIP_NOT_FOUND` | 404 | Relationship ID does not exist | Verify ID |
| `DUPLICATE_NODE` | 409 | Unique constraint violation | Use existing node or different name |
| `INVALID_CYPHER` | 422 | Cypher query contains mutations | Use read-only query |
| `VALIDATION_ERROR` | 400 | Request body validation failed | Fix request body |
| `RATE_LIMITED` | 429 | Too many requests | Wait and retry |
| `NEO4J_ERROR` | 500 | Neo4j query failure | Retry or contact admin |
| `QDRANT_ERROR` | 500 | Qdrant query failure | Retry or contact admin |
| `AI_EXTRACTION_FAILED` | 500 | LLM call failed | Retry with different model |
| `INGESTION_CANCELLED` | 200 | Job was cancelled | Re-trigger if needed |
