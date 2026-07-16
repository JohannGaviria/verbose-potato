"""This module contains the infrastructure composition."""

from collections.abc import AsyncIterator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.cache.redis_client import redis_client
from src.shared.infrastructure.database.database import db
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)


def get_logger_factory_outbound() -> StructlogLoggerFactoryOutboundAdapter:
    """Get the StructlogLoggerFactoryOutboundAdapter instance.

    Returns:
        StructlogLoggerFactoryOutboundAdapter: The StructlogLoggerFactoryOutboundAdapter instance.
    """
    return StructlogLoggerFactoryOutboundAdapter()


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Get a db session context manager.

    Returns:
        AsyncIterator[AsyncSession]: The db session context manager.
    """
    async with db.session() as session:
        yield session


async def get_redis() -> Redis:
    """Get a Redis client.

    Returns:
        Redis: The Redis client.
    """
    return redis_client.client
