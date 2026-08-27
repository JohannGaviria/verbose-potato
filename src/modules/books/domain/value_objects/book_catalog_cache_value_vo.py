"""This module contains the book catalog cache value vo."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.shared.domain.exceptions.cache_exception import InvalidCacheEntryException
from src.shared.domain.value_objects.cache_value_vo import CacheValueVO


@dataclass(frozen=True, slots=True)
class BookCatalogCacheValueVO(CacheValueVO):
    """Value object representing a cached, paginated book catalog result.

    This is the JSON-serializable snapshot stored under the
    ``cache:books:catalog:{filters_hash}`` cache key so that a subsequent
    request for the same filters, sorting, and pagination can be served
    without hitting the database.

    Attributes:
        items (tuple[Mapping[str, Any], ...]): The serialized books for the
            current page.
        total (int): The total number of books matching the filters,
            ignoring pagination.
        page (int): The page number this snapshot corresponds to.
        page_size (int): The number of items per page.
        total_pages (int): The total number of pages available.
    """

    items: tuple[Mapping[str, Any], ...]
    total: int
    page: int
    page_size: int
    total_pages: int

    def _validate(self) -> None:
        """Validate the rules for the book catalog cache value object.

        The rules for the book catalog cache value object are:
        - Items must be a tuple.
        - Total must be an integer.
        - Total cannot be negative.
        - Page must be an integer.
        - Page must be greater than or equal to 1.
        - Page size must be an integer.
        - Page size must be greater than or equal to 1.
        - Total pages must be an integer.
        - Total pages cannot be negative.

        Raises:
            InvalidCacheEntryException: If the cache value does not meet the
                validation criteria.
        """
        if not isinstance(self.items, tuple):
            raise InvalidCacheEntryException("items must be a tuple.")
        if not isinstance(self.total, int) or isinstance(self.total, bool):
            raise InvalidCacheEntryException("total must be an integer.")
        if self.total < 0:
            raise InvalidCacheEntryException("total cannot be negative.")
        if not isinstance(self.page, int) or isinstance(self.page, bool):
            raise InvalidCacheEntryException("page must be an integer.")
        if self.page < 1:
            raise InvalidCacheEntryException("page must be greater than or equal to 1.")
        if not isinstance(self.page_size, int) or isinstance(self.page_size, bool):
            raise InvalidCacheEntryException("page_size must be an integer.")
        if self.page_size < 1:
            raise InvalidCacheEntryException(
                "page_size must be greater than or equal to 1."
            )
        if not isinstance(self.total_pages, int) or isinstance(self.total_pages, bool):
            raise InvalidCacheEntryException("total_pages must be an integer.")
        if self.total_pages < 0:
            raise InvalidCacheEntryException("total_pages cannot be negative.")

    def to_dict(self) -> dict[str, Any]:
        """Convert the cache value to a JSON-serializable dictionary.

        Returns:
            dict[str, Any]: The dictionary representation of the cached book
                catalog result.
        """
        return {
            "items": [dict(item) for item in self.items],
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "BookCatalogCacheValueVO":
        """Reconstruct a book catalog cache value from its dictionary representation.

        The dictionary is expected to contain the data returned by the cache adapter
        after JSON decoding.

        Args:
            data (Mapping[str, Any]): The raw cached data.

        Returns:
            BookCatalogCacheValueVO: The rebuilt cache value.
        """
        return cls(
            items=tuple(data["items"]),
            total=data["total"],
            page=data["page"],
            page_size=data["page_size"],
            total_pages=data["total_pages"],
        )
