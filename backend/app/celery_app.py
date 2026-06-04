"""Celery application configuration."""

from celery import Celery
from app.config import settings

celery_app = Celery(
    "torah_knowledge_graph",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600 * 4,  # 4 hours for long extraction jobs
    worker_prefetch_multiplier=1,
    task_default_queue="default",
    task_routes={
        "app.tasks.extract_from_sefaria": {"queue": "extraction"},
        "app.tasks.transform_book": {"queue": "etl"},
        "app.tasks.load_to_neo4j": {"queue": "etl"},
        "app.tasks.embed_verses": {"queue": "embedding"},
    },
)
