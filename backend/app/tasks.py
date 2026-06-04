"""Celery background tasks for ingestion pipeline."""

import asyncio
import json
import time
from pathlib import Path

import httpx
import structlog
from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import IngestionJob, JobStatus
from app.neo4j_client import get_driver

logger = structlog.get_logger()

# Sync engine for Celery tasks to update job status
sync_engine = create_engine(
    settings.database_url.replace("+asyncpg", ""),
    pool_pre_ping=True,
)
SyncSession = sessionmaker(bind=sync_engine)


SEFARIA_API_BASE = "https://www.sefaria.org/api"
RATE_LIMIT_SECONDS = 1.1
RAW_DIR = Path("/app/data/raw")
PROCESSED_DIR = Path("/app/data/processed")


def _update_job(job_id, **kwargs):
    with SyncSession() as session:
        job = session.get(IngestionJob, job_id)
        if not job:
            return
        for key, value in kwargs.items():
            setattr(job, key, value)
        session.commit()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def extract_from_sefaria(self, job_id: str, book_title: str):
    """Fetch a single book from Sefaria API chapter by chapter."""
    job_uuid = job_id
    _update_job(job_uuid, status=JobStatus.RUNNING)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("sefaria_extraction_started", job=job_uuid, book=book_title)

    try:
        # Fetch index
        index_url = f"{SEFARIA_API_BASE}/index/{book_title.replace(' ', '%20')}"
        resp = httpx.get(index_url, timeout=30)
        resp.raise_for_status()
        index_data = resp.json()

        schema = index_data.get("schema", {})
        lengths = schema.get("lengths", [])
        total_chapters = int(lengths[0]) if lengths else schema.get("length", 1)
        section_names = schema.get("sectionNames", ["Chapter"])
        hebrew_title = index_data.get("heTitle", "")
        category = index_data.get("categories", [])

        _update_job(job_uuid, total_refs=total_chapters, fetched_refs=0, failed_refs=0)

        book_data = {
            "title": book_title,
            "hebrew_title": hebrew_title,
            "category": category,
            "schema": schema,
            "refs": {},
            "extraction_meta": {
                "total_refs": total_chapters,
                "fetched_refs": 0,
                "failed_refs": 0,
                "source": "Sefaria.org",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        }

        errors = []

        for i in range(1, total_chapters + 1):
            ref = f"{book_title} {i}"
            ref_data = {}

            time.sleep(RATE_LIMIT_SECONDS)
            try:
                he_resp = httpx.get(
                    f"{SEFARIA_API_BASE}/texts/{ref.replace(' ', '%20')}",
                    params={"lang": "he"},
                    timeout=30,
                )
                he_resp.raise_for_status()
                ref_data["hebrew"] = he_resp.json()
            except Exception as e:
                ref_data["hebrew_error"] = str(e)
                errors.append({"ref": ref, "lang": "he", "error": str(e)})
                book_data["extraction_meta"]["failed_refs"] += 1

            time.sleep(RATE_LIMIT_SECONDS)
            try:
                en_resp = httpx.get(
                    f"{SEFARIA_API_BASE}/texts/{ref.replace(' ', '%20')}",
                    params={"lang": "en"},
                    timeout=30,
                )
                en_resp.raise_for_status()
                ref_data["english"] = en_resp.json()
            except Exception as e:
                ref_data["english_error"] = str(e)
                errors.append({"ref": ref, "lang": "en", "error": str(e)})
                book_data["extraction_meta"]["failed_refs"] += 1

            book_data["refs"][ref] = ref_data
            book_data["extraction_meta"]["fetched_refs"] += 1

            # Update progress every chapter
            _update_job(
                job_uuid,
                fetched_refs=book_data["extraction_meta"]["fetched_refs"],
                failed_refs=book_data["extraction_meta"]["failed_refs"],
                errors=errors,
            )

        # Save raw JSON
        safe_title = book_title.replace(" ", "_").replace(",", "").replace("/", "_")
        output_file = RAW_DIR / f"{safe_title}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)

        _update_job(
            job_uuid,
            status=JobStatus.COMPLETED,
            meta={"raw_file": str(output_file), "total_refs": total_chapters},
        )
        logger.info("sefaria_extraction_complete", job=job_uuid, book=book_title)

        # Trigger transform
        transform_book.delay(job_uuid, str(output_file))

    except Exception as exc:
        logger.error("sefaria_extraction_failed", job=job_uuid, error=str(exc))
        _update_job(job_uuid, status=JobStatus.FAILED, errors=[{"error": str(exc)}])
        raise self.retry(exc=exc)


@shared_task
def transform_book(job_id: str, raw_file_path: str):
    """Convert raw Sefaria JSON to Neo4j-ready JSONL."""
    from scripts.transform_for_neo4j import transform_tanakh

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    result = transform_tanakh(Path(raw_file_path), PROCESSED_DIR)
    logger.info("transform_complete", job=job_id, result=result)

    # Trigger Neo4j load
    load_to_neo4j.delay(
        job_id,
        result["nodes_file"],
        result["relationships_file"],
    )


@shared_task
def load_to_neo4j(job_id: str, nodes_file: str, relationships_file: str):
    """Load processed JSONL into Neo4j via async UNWIND batches."""

    async def _load():
        driver = await get_driver()
        nodes_path = Path(nodes_file)
        rels_path = Path(relationships_file)

        # Load nodes
        nodes = []
        with open(nodes_path, "r", encoding="utf-8") as f:
            for line in f:
                nodes.append(json.loads(line))

        batch_size = 500
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i : i + batch_size]
            async with driver.session() as session:
                await session.run(
                    """
                    UNWIND $batch AS node
                    CALL apoc.merge.node(
                        [node.label],
                        {id: node.id},
                        node.properties
                    ) YIELD node as n
                    RETURN count(n)
                    """,
                    batch=batch,
                )
            logger.info("neo4j_nodes_loaded", batch=i // batch_size, count=len(batch))

        # Load relationships
        rels = []
        with open(rels_path, "r", encoding="utf-8") as f:
            for line in f:
                rels.append(json.loads(line))

        for i in range(0, len(rels), batch_size):
            batch = rels[i : i + batch_size]
            async with driver.session() as session:
                await session.run(
                    """
                    UNWIND $batch AS rel
                    MATCH (a {id: rel.from_id})
                    MATCH (b {id: rel.to_id})
                    CALL apoc.merge.relationship(
                        a,
                        rel.type,
                        {},
                        rel.properties,
                        b
                    ) YIELD rel as r
                    RETURN count(r)
                    """,
                    batch=batch,
                )
            logger.info("neo4j_rels_loaded", batch=i // batch_size, count=len(batch))

    asyncio.run(_load())
    logger.info("neo4j_load_complete", job=job_id)

    # Trigger embedding
    embed_verses.delay(job_id, nodes_file)


@shared_task
def embed_verses(job_id: str, nodes_file: str):
    """Generate embeddings and upsert into Qdrant."""
    if not settings.openai_api_key:
        logger.info("embed_verses_skipped_no_api_key", job=job_id)
        return

    import openai
    from qdrant_client import QdrantClient

    client = openai.OpenAI(api_key=settings.openai_api_key)
    qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

    nodes = []
    with open(nodes_file, "r", encoding="utf-8") as f:
        for line in f:
            node = json.loads(line)
            if node.get("label") == "Verse":
                nodes.append(node)

    if not nodes:
        logger.info("embed_verses_no_verses", job=job_id)
        return

    batch_size = 100
    for i in range(0, len(nodes), batch_size):
        batch = nodes[i : i + batch_size]
        texts = [
            f"{n['properties'].get('text_hebrew', '')}\n{n['properties'].get('text_english', '')}"
            for n in batch
        ]
        resp = client.embeddings.create(
            input=texts, model=settings.embedding_model
        )
        vectors = [d.embedding for d in resp.data]

        points = []
        for n, vec in zip(batch, vectors):
            points.append({
                "id": n["id"],
                "vector": vec,
                "payload": {
                    "neo4j_node_id": n["id"],
                    "node_type": "Verse",
                    "book": n["properties"].get("book"),
                    "chapter": n["properties"].get("chapter"),
                    "verse_number": n["properties"].get("verse_number"),
                    "ref": n["properties"].get("ref"),
                },
            })

        qdrant.upsert(collection_name="torah_verses", points=points)
        logger.info("qdrant_upserted", job=job_id, batch=i // batch_size, count=len(batch))

    logger.info("embed_verses_complete", job=job_id, total=len(nodes))
