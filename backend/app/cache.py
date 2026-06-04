from functools import wraps
import time
import hashlib
import json
from typing import Any, Callable, Optional

class RedisCache:
    """Enterprise-grade Redis caching with TTL, tags, and invalidation."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._client = None

    async def get_client(self):
        if self._client is None:
            import redis.asyncio as redis
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate deterministic cache key."""
        content = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"tkg:{prefix}:{hash_val}"

    async def get(self, key: str) -> Optional[str]:
        client = await self.get_client()
        return await client.get(key)

    async def set(self, key: str, value: str, ttl_seconds: int = 300, tags: list = None):
        """Set cache value with TTL and optional tags for grouped invalidation."""
        client = await self.get_client()
        pipe = client.pipeline()
        pipe.setex(key, ttl_seconds, value)
        if tags:
            for tag in tags:
                pipe.sadd(f"tkg:tag:{tag}", key)
        await pipe.execute()

    async def delete(self, key: str):
        client = await self.get_client()
        await client.delete(key)

    async def invalidate_tag(self, tag: str):
        """Invalidate all keys associated with a tag."""
        client = await self.get_client()
        keys = await client.smembers(f"tkg:tag:{tag}")
        if keys:
            pipe = client.pipeline()
            for key in keys:
                pipe.delete(key)
            pipe.delete(f"tkg:tag:{tag}")
            await pipe.execute()

    async def invalidate_pattern(self, pattern: str):
        """Invalidate keys matching a pattern."""
        client = await self.get_client()
        keys = []
        cursor = 0
        while True:
            cursor, batch = await client.scan(cursor, match=pattern, count=100)
            keys.extend(batch)
            if cursor == 0:
                break
        if keys:
            await client.delete(*keys)

    def cached(self, prefix: str, ttl_seconds: int = 300, tags: list = None):
        """Decorator for caching function results."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Skip cache for non-idempotent requests
                cache_key = self._make_key(prefix, *args, **kwargs)

                try:
                    cached = await self.get(cache_key)
                    if cached is not None:
                        from app.routers.metrics import metrics_collector
                        metrics_collector.record_cache_hit(prefix)
                        return json.loads(cached)
                except Exception:
                    pass  # Cache error shouldn't break the app

                result = await func(*args, **kwargs)

                try:
                    await self.set(
                        cache_key,
                        json.dumps(result, default=str),
                        ttl_seconds=ttl_seconds,
                        tags=tags
                    )
                    from app.routers.metrics import metrics_collector
                    metrics_collector.record_cache_miss(prefix)
                except Exception:
                    pass

                return result
            return wrapper
        return decorator

# Global cache instance
cache = RedisCache()
