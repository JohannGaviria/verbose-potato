"""This module contains the book cache catalog key value object."""

from dataclasses import dataclass

from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO


@dataclass(frozen=True, slots=True)
class BookCatalogCacheKeyVO(CacheKeyVO):
    """Value object representing the base cache key pattern for the book catalog.

    Attributes:
        key (str): The base cache key pattern.
    """

    key: str

    @classmethod
    def pattern(cls) -> "BookCatalogCacheKeyVO":
        """Create the base cache key pattern for the book catalog.

        Returns:
            BookCatalogCacheKeyVO: The base cache key pattern.
        """
        key = "cache:books:catalog"
        return cls(key=key)
