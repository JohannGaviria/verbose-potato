"""This module contains the cache key vo class."""

import re
from dataclasses import dataclass

from src.shared.domain.exceptions.cache_exception import InvalidCacheKeyException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class CacheKeyVO(BaseValueObject):
    """Value Object for cache keys.

    The cache key must follow the pattern: ``cache:{type}:{id}[:{optional}]``

    Examples of valid keys:
        cache:user:123
        cache:session:abc:def

    Constraints:
        - Must start with "cache:"
        - Followed by a type (alphanumeric or underscore)
        - Followed by an ID (alphanumeric or underscore)
        - Optionally followed by additional segments (e.g., :extra)
        - Maximum length of 250 characters

    Attributes:
        key (str): The cache key string.
    """

    key: str

    def _validate(self) -> None:
        """Validate the cache key against defined rules.

        Raises:
            InvalidCacheKeyException: If the cache key does not meet the validation criteria.
        """
        # Regex pattern:
        # Example valid keys: cache:user:123, cache:session:abc:def
        CACHE_PATTERN = r"^cache:[^:\s]+:[^:\s]+(:[^:\s]+)?$"

        if self.key is None:
            raise InvalidCacheKeyException("Cache key cannot be None.")
        if not isinstance(self.key, str):
            raise InvalidCacheKeyException("Cache key must be a string.")
        if not self.key.strip():
            raise InvalidCacheKeyException("Cache key cannot be empty.")
        if not re.match(CACHE_PATTERN, self.key):
            raise InvalidCacheKeyException("Cache key must match the pattern.")
        if len(self.key) > 255:
            raise InvalidCacheKeyException(
                "Cache key cannot be longer than 255 characters."
            )

    def value(self) -> str:
        """Return the value of the cache key.

        Returns:
            str: The value of the cache key.
        """
        return self.key
