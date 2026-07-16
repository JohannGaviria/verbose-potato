"""This module contains the redis client class."""

from __future__ import annotations

import redis.asyncio as redis
import structlog
from redis.asyncio import Redis

from src.config import settings


class RedisClient:
    """Manages Redis connections and sessions."""

    def __init__(self) -> None:
        """Initializes the Redis client."""
        self._pool: redis.ConnectionPool | None = None
        self._client: Redis | None = None
        self._logger = structlog.get_logger(__name__)

    def connect(self) -> None:
        """Creates the Redis client. Idempotent."""
        if self._client is not None:
            self._logger.debug("Redis already connected.")
            return

        self._logger.debug("Connecting to Redis...")
        self._pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=settings.REDIS_DECODE_RESPONSES,
        )
        self._client = redis.Redis(connection_pool=self._pool)
        self._logger.debug("Redis connected.")

    async def disconnect(self) -> None:
        """Closes the Redis connection pool. Idempotent."""
        if self._client is not None:
            self._logger.debug("Disconnecting from Redis...")
            await self._client.aclose()
        if self._pool is not None:
            self._logger.debug("Closing Redis connection pool...")
            await self._pool.disconnect()
        self._client = None
        self._pool = None
        self._logger.debug("Redis disconnected.")

    async def ping(self) -> bool:
        """Check if the Redis server is available."""
        self._logger.debug("Pinging Redis...")
        return bool(await self.client.ping())

    @property
    def client(self) -> Redis:
        """Get the Redis client.

        Returns:
            Redis: The Redis client.
        """
        if self._client is None:
            self._logger.debug("Redis not connected. Calling connect()...")
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._client


redis_client = RedisClient()
