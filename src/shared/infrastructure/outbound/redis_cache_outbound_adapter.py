"""This module contains the RedisCacheOutboundAdapter class."""

import json
from collections.abc import Callable

from redis.asyncio import Redis, RedisError

from src.shared.domain.exceptions.cache_exception import (
    CacheDeletionException,
    CacheRetrievalException,
    CacheStorageException,
)
from src.shared.domain.ports.outbound.cache_outbound_port import (
    CacheOutboundPort,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO
from src.shared.domain.value_objects.cache_value_vo import CacheValueVO


class RedisCacheOutboundAdapter[CacheValueType: CacheValueVO](
    CacheOutboundPort[CacheValueType]
):
    """Adapter for interacting with Redis as a cache."""

    def __init__(
        self,
        redis_client: Redis,
        factory: Callable[[dict], CacheValueType],
        logger_factory_outbound: LoggerFactoryOutboundPort,
    ) -> None:
        """Initializes the RedisCacheOutboundAdapter.

        Args:
            redis_client (Redis): The Redis client used for cache operations.
            factory (Callable[[dict], CacheValueType]): A factory function that takes
                a dictionary and returns an instance of CacheValueType.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                used to create a logger for this adapter.
        """
        self._redis_client = redis_client
        self._factory = factory
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def get(self, key: CacheKeyVO) -> CacheValueType | None:
        """Retrieves a cache entry from Redis based on the provided cache key.

        Args:
            key (CacheKeyVO): The cache key of the entry to be retrieved.

        Returns:
            CacheValueType | None: The value associated with
                the cache key if found, otherwise None.
        """
        try:
            value = await self._redis_client.get(str(key))
            if value is None:
                self._logger.debug("Cache entry not found for key.", key=str(key))
                return None
            data = json.loads(value)

            self._logger.debug(
                "Cache entry retrieved successfully for key.", key=str(key)
            )

            return self._factory(data)
        except json.JSONDecodeError as exc:
            self._logger.error(
                "Failed to decode JSON from cache for key.",
                key=str(key),
                exc_info=str(exc),
            )
            raise CacheRetrievalException(
                f"Failed to decode JSON from cache for key: {str(key)}"
            ) from exc
        except RedisError as exc:
            self._logger.error(
                "Redis error occurred while retrieving cache for key.",
                key=str(key),
                exc_info=str(exc),
            )
            raise CacheRetrievalException(
                f"Redis error occurred while retrieving cache for key: {str(key)}"
            ) from exc
        except Exception as exc:
            self._logger.error(
                "Unexpected error occurred while retrieving cache for key.",
                key=str(key),
                exc_info=str(exc),
            )
            raise CacheRetrievalException(
                f"Unexpected error occurred while retrieving cache for key: {str(key)}"
            ) from exc

    async def set(self, entry: CacheEntryVO[CacheValueType]) -> None:
        """Stores a cache entry in Redis with the specified key, value, and TTL.

        Args:
            entry (CacheEntryVO[CacheValueType]): The cache entry to be stored, containing
                the cache key, value, and time-to-live (TTL).

        Raises:
            CacheStorageException: If there is an error during the storage process,
                such as a Redis error, JSON serialization error, or an unexpected exception.
        """
        try:
            await self._redis_client.set(
                name=str(entry.key),
                value=json.dumps(entry.value.to_dict()),
                ex=entry.ttl.seconds,
            )
            self._logger.debug(
                "Cache entry stored successfully for key.", key=str(entry.key)
            )
        except (TypeError, ValueError) as exc:
            self._logger.error(
                "Failed to serialize cache value to JSON for key.",
                key=str(entry.key),
                exc_info=str(exc),
            )
            raise CacheStorageException(
                f"Failed to serialize cache value to JSON for key: {str(entry.key)}"
            ) from exc
        except RedisError as exc:
            self._logger.error(
                "Redis error occurred while storing cache for key.",
                key=str(entry.key),
                exc_info=str(exc),
            )
            raise CacheStorageException(
                f"Redis error occurred while storing cache for key: {str(entry.key)}"
            ) from exc
        except Exception as exc:
            self._logger.error(
                "Unexpected error occurred while storing cache for key.",
                key=str(entry.key),
                exc_info=str(exc),
            )
            raise CacheStorageException(
                f"Unexpected error occurred while storing cache for key: {str(entry.key)}"
            ) from exc

    async def delete(self, key: CacheKeyVO) -> None:
        """Deletes a cache entry from Redis based on the provided cache key.

        Args:
            key (CacheKeyVO): The cache key of the entry to be deleted.

        Raises:
            CacheDeletionException: If there is an error during the deletion process,
                such as a Redis error or an unexpected exception.
        """
        try:
            await self._redis_client.delete(str(key))
            self._logger.info("Cache entry deleted successfully for key.", key=str(key))
        except RedisError as exc:
            self._logger.error(
                "Redis error occurred while deleting cache for key.",
                key=str(key),
                exc_info=str(exc),
            )
            raise CacheDeletionException(
                f"Redis error occurred while deleting cache for key: {str(key)}"
            ) from exc
        except Exception as exc:
            self._logger.error(
                "Unexpected error occurred while deleting cache for key.",
                key=str(key),
                exc_info=str(exc),
            )
            raise CacheDeletionException(
                f"Unexpected error occurred while deleting cache for key: {str(key)}"
            ) from exc
