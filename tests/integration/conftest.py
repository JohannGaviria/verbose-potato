from collections.abc import AsyncIterator

import pytest_asyncio
from redis.asyncio import Redis

from src.shared.infrastructure.cache.redis_client import redis_client as _redis_client
from src.shared.infrastructure.database.database import db as _db


@pytest_asyncio.fixture
async def db() -> AsyncIterator[object]:
    """Provide a connected ``Database`` instance backed by a real PostgreSQL."""
    _db.connect()
    try:
        yield _db
    finally:
        await _db.disconnect()


@pytest_asyncio.fixture
async def redis_conn() -> AsyncIterator[Redis]:
    """Provide a connected Redis client backed by a real Redis instance."""
    _redis_client.connect()
    try:
        yield _redis_client.client
    finally:
        await _redis_client.disconnect()
