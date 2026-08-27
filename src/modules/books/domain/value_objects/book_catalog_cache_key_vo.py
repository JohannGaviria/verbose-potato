"""This module contains the book cache catalog key value object."""

import hashlib
from dataclasses import dataclass

from src.modules.books.domain.value_objects.book_catalog_query_vo import (
    BookCatalogQueryVO,
)
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO


@dataclass(frozen=True, slots=True)
class BookCatalogCacheKeyVO(CacheKeyVO):
    """Value object representing the base cache key pattern for the book catalog.

    Attributes:
        key (str): The base cache key pattern.
    """

    key: str

    _PREFIX = "cache:books:catalog"

    @classmethod
    def pattern(cls) -> "BookCatalogCacheKeyVO":
        """Create the base cache key pattern for the book catalog.

        Returns:
            BookCatalogCacheKeyVO: The base cache key pattern.
        """
        return cls(key=cls._PREFIX)

    @classmethod
    def from_filters(cls, query: BookCatalogQueryVO) -> "BookCatalogCacheKeyVO":
        """Create the cache key for the book catalog, including its search filters.

        Args:
            query (BookCatalogQueryVO): The book catalog query.

        Returns:
            BookCatalogCacheKeyVO: The cache key pattern.
        """
        canonical = "|".join(
            [
                f"title={query.title.value if query.title is not None else ''}",
                f"author={query.author.value if query.author is not None else ''}",
                f"isbn={query.isbn.value if query.isbn is not None else ''}",
                f"available_only={query.is_available if query.is_available is not None else ''}",
                f"sort_by={query.sort_by.value if query.sort_by is not None else ''}",
                f"sort_order={query.sort_order.value if query.sort_order is not None else ''}",
                f"page={query.page}",
                f"page_size={query.page_size}",
            ]
        )
        query_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        key = f"{cls._PREFIX}:{query_hash}"

        return cls(key=key)
