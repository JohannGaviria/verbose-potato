"""This module contains the loan catalog cache key value object."""

from dataclasses import dataclass

from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO


@dataclass(frozen=True, slots=True)
class LoanCatalogCacheKeyVO(CacheKeyVO):
    """Value object representing the base cache key pattern for the loan catalog.

    Attributes:
        key (str): The base cache key pattern.
    """

    key: str

    _PREFIX = "cache:loans:catalog"

    @classmethod
    def pattern(cls) -> "LoanCatalogCacheKeyVO":
        """Create the base cache key pattern for the loan catalog.

        Returns:
            LoanCatalogCacheKeyVO: The base cache key pattern.
        """
        return cls(key=cls._PREFIX)
