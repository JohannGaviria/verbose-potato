"""This module contains the cache entry vo class."""

from dataclasses import dataclass

from src.shared.domain.exceptions.cache_exception import InvalidCacheEntryException
from src.shared.domain.value_objects.base_value_object import BaseValueObject
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO
from src.shared.domain.value_objects.cache_value_vo import CacheValueVO


@dataclass(frozen=True)
class CacheEntryVO[CacheValueType: CacheValueVO](BaseValueObject):
    """Value object representing a cache entry, containing a key, TTL, and value.

    Attributes:
        key (CacheKeyVO): The cache key.
        ttl (CacheTTLVO): The time-to-live for the cache entry.
        value (CacheValueType): The value to be cached,
            which must be a subclass of CacheValueVO.
    """

    key: CacheKeyVO
    ttl: CacheTTLVO
    value: CacheValueType

    def _validate(self) -> None:
        """Validates the cache entry data, ensuring that the key, TTL, and value are all valid.

        Raises:
            InvalidCacheEntryException: If any of the validation checks fail,
                an exception is raised containing the list of validation errors.
        """
        if self.key is None:
            raise InvalidCacheEntryException("Key cannot be None.")
        if self.ttl is None:
            raise InvalidCacheEntryException("TTL cannot be None.")
        if self.value is None:
            raise InvalidCacheEntryException("Value cannot be None.")
        if not isinstance(self.key, CacheKeyVO):
            raise InvalidCacheEntryException("Key must be a CacheKeyVO instance.")
        if not isinstance(self.ttl, CacheTTLVO):
            raise InvalidCacheEntryException("TTL must be a CacheTTLVO instance.")
        if not isinstance(self.value, CacheValueVO):
            raise InvalidCacheEntryException("Value must be a CacheValueVO instance.")
