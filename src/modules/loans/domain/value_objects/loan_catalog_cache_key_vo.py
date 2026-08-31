"""This module contains the loan catalog cache key value object."""

import hashlib
from dataclasses import dataclass

from src.modules.loans.domain.value_objects.loan_catalog_query_vo import (
    LoanCatalogQueryVO,
)
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

    @classmethod
    def from_filters(cls, query: LoanCatalogQueryVO) -> "LoanCatalogCacheKeyVO":
        """Create the cache key for the loan catalog, including its filters.

        Args:
            query (LoanCatalogQueryVO): The loan catalog query.

        Returns:
            LoanCatalogCacheKeyVO: The cache key built from the filters.
        """
        canonical = "|".join(
            [
                f"member_id={query.member_id if query.member_id is not None else ''}",
                f"book_id={query.book_id if query.book_id is not None else ''}",
                f"status={query.status.value if query.status is not None else ''}",
                f"sort_by={query.sort_by.value if query.sort_by is not None else ''}",
                f"sort_order={query.sort_order.value if query.sort_order is not None else ''}",
                f"page={query.page}",
                f"page_size={query.page_size}",
            ]
        )
        query_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        key = f"{cls._PREFIX}:{query_hash}"
        return cls(key=key)
