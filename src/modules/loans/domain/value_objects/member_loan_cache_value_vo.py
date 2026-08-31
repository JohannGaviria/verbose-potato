"""This module contains the member loan cache value vo."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.shared.domain.exceptions.cache_exception import InvalidCacheEntryException
from src.shared.domain.value_objects.cache_value_vo import CacheValueVO


@dataclass(frozen=True, slots=True)
class MemberLoanCacheValueVO(CacheValueVO):
    """Value object representing a cached, paginated loans result for a member.

    This is the JSON-serializable snapshot stored under the
    ``cache:loans:member:{member_id}:{filters_hash}`` cache key so that a
    subsequent request for the same member, filters, sorting, and pagination
    can be served without hitting the database.

    Attributes:
        items (tuple[Mapping[str, Any], ...]): The serialized loans for the
            current page.
        total (int): The total number of loans matching the filters,
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
        """Validate the rules for the member loan cache value object.

        The rules for the member loan cache value object are:
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
            dict[str, Any]: The dictionary representation of the cached member
                loans result.
        """
        return {
            "items": [dict(item) for item in self.items],
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "MemberLoanCacheValueVO":
        """Reconstruct a member loan cache value from its dictionary representation.

        The dictionary is expected to contain the data returned by the cache adapter
        after JSON decoding.

        Args:
            data (Mapping[str, Any]): The raw cached data.

        Returns:
            MemberLoanCacheValueVO: The rebuilt cache value.
        """
        return cls(
            items=tuple(data["items"]),
            total=data["total"],
            page=data["page"],
            page_size=data["page_size"],
            total_pages=data["total_pages"],
        )
