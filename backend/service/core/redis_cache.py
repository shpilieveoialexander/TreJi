from typing import Iterator, Optional

import ujson
from redis import Redis

from .settings import settings


class RedisClient:
    """A simple redis client for storing and retrieving native python datatypes."""

    def __init__(self):
        """Initialize client."""
        self.client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )

    def set(self, key: str, val: str | dict, exp: int = 10) -> None:
        """Store a value in Redis."""
        return self.client.set(key, ujson.dumps(val), ex=exp * 60)

    def get(self, key: str) -> Optional[str | dict]:
        """Retrieve a value from Redis."""
        val = self.client.get(key)
        if not val:
            return
        return ujson.loads(val)

    def keys(self, template: str) -> Iterator:
        """Retrieve all keys simular to template"""
        return self.client.scan_iter(template)

    def pop(self, key: str) -> Optional[str | dict]:
        """Delete and return a value from Redis."""
        val = self.client.getdel(key)
        if not val:
            return
        return ujson.loads(val)


redis_cache = RedisClient()
