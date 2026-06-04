from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response
import time

router = APIRouter(tags=["metrics"])

# HTTP metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Graph metrics
graph_query_duration_seconds = Histogram(
    "graph_query_duration_seconds",
    "Neo4j graph query duration",
    ["query_type"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

graph_nodes_total = Gauge(
    "graph_nodes_total",
    "Total nodes in graph",
    ["node_type"]
)

graph_relationships_total = Gauge(
    "graph_relationships_total",
    "Total relationships in graph",
    ["rel_type"]
)

# AI metrics
ai_chat_requests_total = Counter(
    "ai_chat_requests_total",
    "Total AI chat requests",
    ["provider", "model"]
)

ai_chat_tokens_total = Counter(
    "ai_chat_tokens_total",
    "Total AI chat tokens",
    ["provider"]
)

ai_chat_duration_seconds = Histogram(
    "ai_chat_duration_seconds",
    "AI chat response duration",
    ["provider"],
    buckets=[1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

# Search metrics
search_requests_total = Counter(
    "search_requests_total",
    "Total search requests",
    ["search_type", "index_used"]
)

search_duration_seconds = Histogram(
    "search_duration_seconds",
    "Search duration",
    ["search_type"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

# Cache metrics
cache_hits_total = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["cache_name"]
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total cache misses",
    ["cache_name"]
)

# Business metrics
verses_searched_total = Counter(
    "verses_searched_total",
    "Total verses returned in search results"
)

active_users_online = Gauge(
    "active_users_online",
    "Currently active users"
)

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

class MetricsCollector:
    """Helper to collect metrics from the application."""

    @staticmethod
    def record_graph_query(query_type: str, duration: float):
        graph_query_duration_seconds.labels(query_type=query_type).observe(duration)

    @staticmethod
    def record_search(search_type: str, index_used: str, duration: float):
        search_requests_total.labels(search_type=search_type, index_used=index_used).inc()
        search_duration_seconds.labels(search_type=search_type).observe(duration)

    @staticmethod
    def record_ai_chat(provider: str, model: str, duration: float, tokens: int = 0):
        ai_chat_requests_total.labels(provider=provider, model=model).inc()
        ai_chat_duration_seconds.labels(provider=provider).observe(duration)
        if tokens:
            ai_chat_tokens_total.labels(provider=provider).inc(tokens)

    @staticmethod
    def record_cache_hit(cache_name: str):
        cache_hits_total.labels(cache_name=cache_name).inc()

    @staticmethod
    def record_cache_miss(cache_name: str):
        cache_misses_total.labels(cache_name=cache_name).inc()

metrics_collector = MetricsCollector()
