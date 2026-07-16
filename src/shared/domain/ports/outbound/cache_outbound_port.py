"""This module contains the cache outbound port class."""

from abc import ABC, abstractmethod

from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO
from src.shared.domain.value_objects.cache_value_vo import CacheValueVO


class CacheOutboundPort[CacheValueType: CacheValueVO](ABC):
    """Outbound port for cache operations.

    Defining the interface for interacting with a cache system.
    """

    @abstractmethod
    async def get(self, key: CacheKeyVO) -> CacheValueType | None:
        """Get a value from the cache by its key.

        Args:
            key (CacheKeyVO): The key of the cache entry to retrieve.

        Returns:
            CacheValueType | None: The value associated with the key, or None if the key
        """
        pass

    @abstractmethod
    async def set(self, entry: CacheEntryVO[CacheValueType]) -> None:
        """Set a value in the cache with the given key and value.

        Args:
            entry (CacheEntryVO[CacheValueType]): The cache entry containing
                the key, ttl, and value to be set.
        """
        pass

    @abstractmethod
    async def delete(self, key: CacheKeyVO) -> None:
        """Delete a value from the cache by its key.

        Args:
            key (CacheKeyVO): The key of the cache entry to delete.
        """
        pass
