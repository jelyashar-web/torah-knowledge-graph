from fastapi import Request, Response
import time
from app.routers.metrics import http_requests_total, http_request_duration_seconds

class MetricsMiddleware:
    """ASGI middleware to collect HTTP metrics."""

    async def __call__(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code

        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()

        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        return response
