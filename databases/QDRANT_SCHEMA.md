# Torah Knowledge Graph — Qdrant Vector Schema

## Overview

Qdrant serves as the platform's vector search engine, enabling semantic retrieval over Torah text passages and entity embeddings. This document specifies two collections, their vector configurations, payload schemas, indexing strategies, and the synchronization pipeline from Neo4j.

**Embedding Model:** `intfloat/multilingual-e5-large`  
**Vector Dimension:** 768  
**Distance Metric:** Cosine

---

## Collection 1: `torah_texts`

Purpose: Semantic search over Torah text passages (verses, paragraphs, sections).

### Vector Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `size` | 768 | Matches multilingual-e5-large output |
| `distance` | Cosine | Standard for semantic similarity |
| `on_disk` | true | Store vectors on disk for large collections |
| `multivector_config` | null | Single vector per point |

### Payload Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text_id` | string (UUID) | yes | References PostgreSQL `texts.id` |
| `source_id` | string (UUID) | yes | References PostgreSQL `sources.id` |
| `title` | string | yes | Human-readable source title |
| `hebrew_title` | string | no | Original Hebrew title |
| `content` | string | yes | Raw text content (truncated to 512 chars for preview) |
| `language` | string | yes | `he`, `en`, `ar`, `yi`, `la` |
| `chapter` | string | no | Chapter or section identifier |
| `verse` | string | no | Verse or paragraph identifier |
| `category` | string | no | `Tanakh`, `Mishna`, `Talmud`, `Halakha`, `Kabbalah`, etc. |
| `embedding_model` | string | yes | `multilingual-e5-large` |
| `created_at` | string (ISO 8601) | yes | Embedding creation timestamp |

### HNSW Index Parameters

```json
{
  "hnsw_config": {
    "m": 16,
    "ef_construct": 200,
    "full_scan_threshold": 10000,
    "max_indexing_threads": 4,
    "on_disk": true
  }
}
```

### Payload Indexes

```json
{
  "field_name": "source_id",
  "field_schema": "keyword"
}
```

```json
{
  "field_name": "language",
  "field_schema": "keyword"
}
```

```json
{
  "field_name": "category",
  "field_schema": "keyword"
}
```

```json
{
  "field_name": "created_at",
  "field_schema": "datetime"
}
```

---

## Collection 2: `torah_entities`

Purpose: Entity similarity search — find related people, places, concepts, and things across the corpus.

### Vector Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `size` | 768 | Same embedding space as texts for cross-modal search |
| `distance` | Cosine | |
| `on_disk` | true | |

### Payload Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entity_id` | string (UUID) | yes | References Neo4j node UUID |
| `entity_type` | string | yes | `Person`, `Place`, `Concept`, `Event`, `Object`, `Organization` |
| `name` | string | yes | Canonical English/Hebrew name |
| `hebrew_name` | string | no | Hebrew script name |
| `aliases` | array of strings | no | Alternative names and spellings |
| `description` | string | no | Short generated description |
| `source_ids` | array of strings (UUIDs) | yes | PostgreSQL sources where entity appears |
| `relationship_count` | integer | yes | Number of Neo4j edges |
| `embedding_model` | string | yes | `multilingual-e5-large` |
| `created_at` | string (ISO 8601) | yes | |

### HNSW Index Parameters

Same as `torah_texts`:

```json
{
  "hnsw_config": {
    "m": 16,
    "ef_construct": 200,
    "full_scan_threshold": 10000,
    "max_indexing_threads": 4,
    "on_disk": true
  }
}
```

### Payload Indexes

```json
{
  "field_name": "entity_type",
  "field_schema": "keyword"
}
```

```json
{
  "field_name": "name",
  "field_schema": "text"
}
```

```json
{
  "field_name": "aliases",
  "field_schema": "keyword"
}
```

---

## Collection Initialization

### Via REST API (curl)

```bash
# torah_texts
curl -X PUT 'http://localhost:6333/collections/torah_texts' \
  -H 'Content-Type: application/json' \
  -d '{
    "vectors": {
      "size": 768,
      "distance": "Cosine",
      "on_disk": true
    },
    "hnsw_config": {
      "m": 16,
      "ef_construct": 200,
      "full_scan_threshold": 10000,
      "max_indexing_threads": 4,
      "on_disk": true
    },
    "optimizers_config": {
      "default_segment_number": 2,
      "indexing_threshold": 20000
    }
  }'

# torah_entities
curl -X PUT 'http://localhost:6333/collections/torah_entities' \
  -H 'Content-Type: application/json' \
  -d '{
    "vectors": {
      "size": 768,
      "distance": "Cosine",
      "on_disk": true
    },
    "hnsw_config": {
      "m": 16,
      "ef_construct": 200,
      "full_scan_threshold": 10000,
      "max_indexing_threads": 4,
      "on_disk": true
    }
  }'

# Payload indexes — torah_texts
curl -X PUT 'http://localhost:6333/collections/torah_texts/index' \
  -H 'Content-Type: application/json' \
  -d '{"field_name": "source_id", "field_schema": "keyword"}'

curl -X PUT 'http://localhost:6333/collections/torah_texts/index' \
  -H 'Content-Type: application/json' \
  -d '{"field_name": "language", "field_schema": "keyword"}'

curl -X PUT 'http://localhost:6333/collections/torah_texts/index' \
  -H 'Content-Type: application/json' \
  -d '{"field_name": "category", "field_schema": "keyword"}'

curl -X PUT 'http://localhost:6333/collections/torah_texts/index' \
  -H 'Content-Type: application/json' \
  -d '{"field_name": "created_at", "field_schema": "datetime"}'

# Payload indexes — torah_entities
curl -X PUT 'http://localhost:6333/collections/torah_entities/index' \
  -H 'Content-Type: application/json' \
  -d '{"field_name": "entity_type", "field_schema": "keyword"}'

curl -X PUT 'http://localhost:6333/collections/torah_entities/index' \
  -H 'Content-Type: application/json' \
  -d '{"field_name": "name", "field_schema": "text"}'

curl -X PUT 'http://localhost:6333/collections/torah_entities/index' \
  -H 'Content-Type: application/json' \
  -d '{"field_name": "aliases", "field_schema": "keyword"}'
```

### Via Python (qdrant-client)

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, HnswConfigDiff

client = QdrantClient(url="http://localhost:6333")

# Create collections
for name in ["torah_texts", "torah_entities"]:
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE, on_disk=True),
        hnsw_config=HnswConfigDiff(
            m=16,
            ef_construct=200,
            full_scan_threshold=10000,
            max_indexing_threads=4,
            on_disk=True,
        ),
        optimizers_config={
            "default_segment_number": 2,
            "indexing_threshold": 20000,
        },
    )

# Create payload indexes — torah_texts
client.create_payload_index("torah_texts", "source_id", "keyword")
client.create_payload_index("torah_texts", "language", "keyword")
client.create_payload_index("torah_texts", "category", "keyword")
client.create_payload_index("torah_texts", "created_at", "datetime")

# Create payload indexes — torah_entities
client.create_payload_index("torah_entities", "entity_type", "keyword")
client.create_payload_index("torah_entities", "name", "text")
client.create_payload_index("torah_entities", "aliases", "keyword")
```

---

## Example Queries

### Semantic Search (texts)

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

results = client.search(
    collection_name="torah_texts",
    query_vector=embedding,  # 768-dim vector from multilingual-e5-large
    query_filter=Filter(
        must=[
            FieldCondition(key="language", match=MatchValue(value="he")),
            FieldCondition(key="category", match=MatchValue(value="Tanakh")),
        ]
    ),
    limit=10,
    with_payload=True,
    search_params={"hnsw_ef": 128},  # higher accuracy for low-latency tolerance
)
```

### Recommend (find similar entities)

```python
from qdrant_client.models import RecommendRequest

results = client.recommend(
    collection_name="torah_entities",
    positive=["entity-uuid-1", "entity-uuid-2"],
    negative=["entity-uuid-3"],
    limit=10,
    with_payload=True,
)
```

### Scroll (batch export for re-indexing)

```python
offset = None
batch_size = 1000

while True:
    records, offset = client.scroll(
        collection_name="torah_texts",
        limit=batch_size,
        offset=offset,
        with_payload=True,
        with_vectors=False,  # set True if re-indexing vectors elsewhere
    )
    if not records:
        break
    process_batch(records)
    if offset is None:
        break
```

### Hybrid Search (vector + keyword payload filter)

```python
results = client.search(
    collection_name="torah_texts",
    query_vector=embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="content",
                match=MatchValue(value="Moses")  # payload keyword match
            ),
        ]
    ),
    limit=20,
)
```

---

## Sync Strategy: Neo4j to Qdrant

### Architecture

```
Neo4j (graph)  -->  ETL Worker  -->  Qdrant (vectors)
     |                |                |
     |                |                |
  Nodes/Edges    Embedding Model   Collections
  (entities)     (e5-large)      (texts, entities)
```

### Sync Modes

| Mode | Trigger | Latency | Use Case |
|------|---------|---------|----------|
| **Real-time** | Neo4j transaction event handler | < 1s | New relationship validated by human |
| **Batch** | Celery cron (every 15 min) | ~15 min | Routine ingestion pipeline |
| **Full Rebuild** | Admin API call | Hours | Model version upgrade, schema change |

### Real-Time Sync (Neo4j APOC Trigger)

```cypher
// Install in Neo4j as a custom trigger via APOC
CALL apoc.trigger.add('sync-to-qdrant',
  "MATCH (r:Relationship)
   WHERE r.synced_to_qdrant IS NULL
   WITH r LIMIT 100
   CALL apoc.load.jsonParams('http://qdrant-sync:8000/sync/relationships',
     {`Content-Type":"application/json"},
     apoc.convert.toJson({relationships: collect(r)})
   ) YIELD value
   SET r.synced_to_qdrant = true
   RETURN count(r)",
  {phase: 'after'}
)
```

> Note: Real-time sync requires the Neo4j APOC plugin and a lightweight HTTP bridge service. For most deployments, **batch sync is sufficient and simpler**.

### Batch Sync (Python / Celery)

```python
# tasks/sync_qdrant.py
from celery import shared_task
from qdrant_client import QdrantClient
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-large")
qdrant = QdrantClient(url="http://qdrant:6333")
neo4j = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "password"))

@shared_task(bind=True, max_retries=3)
def sync_entities_to_qdrant(self, last_sync_ts: str):
    with neo4j.session() as session:
        result = session.run("""
            MATCH (e:Entity)
            WHERE e.updated_at > datetime($last_sync_ts)
            RETURN e.id AS entity_id, e.name AS name,
                   e.hebrew_name AS hebrew_name, e.type AS entity_type,
                   e.description AS description, e.aliases AS aliases
        """, last_sync_ts=last_sync_ts)

        points = []
        for record in result:
            text_to_embed = f"{record['name']} {record['hebrew_name'] or ''} {record['description'] or ''}"
            vector = model.encode(text_to_embed, normalize_embeddings=True).tolist()

            points.append({
                "id": record["entity_id"],
                "vector": vector,
                "payload": {
                    "entity_id": record["entity_id"],
                    "entity_type": record["entity_type"],
                    "name": record["name"],
                    "hebrew_name": record["hebrew_name"],
                    "aliases": record["aliases"] or [],
                    "description": record["description"],
                    "created_at": datetime.utcnow().isoformat(),
                    "embedding_model": "multilingual-e5-large",
                }
            })

        if points:
            qdrant.upsert(collection_name="torah_entities", points=points)

    return {"synced": len(points)}
```

### Sync Checklist

- [ ] Neo4j `updated_at` timestamp maintained on every node/relationship write
- [ ] Celery beat schedule configured for 15-minute batches
- [ ] Dead-letter queue for failed Qdrant upserts
- [ ] Idempotent upserts (Qdrant `upsert` is naturally idempotent by point ID)
- [ ] Monitoring: sync lag metric (`now() - max(created_at)` in Qdrant)
- [ ] Full-rebuild endpoint protected by admin role

---

## Backup & Maintenance

### Snapshot (Qdrant native)

```bash
curl -X POST 'http://localhost:6333/collections/torah_texts/snapshots'
curl -X POST 'http://localhost:6333/collections/torah_entities/snapshots'
```

### Storage Notes

- Vectors are stored on disk (`on_disk: true`) to keep RAM usage manageable.
- HNSW graph is also on disk; first queries after restart may be slower until hot.
- For RAM-constrained environments, consider `m: 8` and `ef_construct: 100`.
- Monitor `/dashboard` for segment count; optimize if > 10 segments per collection.
