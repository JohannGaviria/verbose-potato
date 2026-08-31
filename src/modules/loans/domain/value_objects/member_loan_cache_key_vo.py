"""This module contains the member loan cache key value object."""

import hashlib
from dataclasses import dataclass
from uuid import UUID

from src.modules.loans.domain.value_objects.member_loan_query_vo import (
    MemberLoanQueryVO,
)
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO


@dataclass(frozen=True, slots=True)
class MemberLoanCacheKeyVO(CacheKeyVO):
    """Value object representing the base cache key pattern for the member loans.

    Attributes:
        key (str): The base cache key pattern.
    """

    key: str

    _PREFIX = "cache:loans:member"

    @classmethod
    def for_member(cls, member_id: UUID) -> "MemberLoanCacheKeyVO":
        """Create the base cache key pattern for the loans of the given member.

        Args:
            member_id (UUID): The member identifier.

        Returns:
            MemberLoanCacheKeyVO: The base cache key pattern.
        """
        return cls(key=f"{cls._PREFIX}:{member_id}")

    @classmethod
    def from_filters(
        cls, member_id: UUID, query: MemberLoanQueryVO
    ) -> "MemberLoanCacheKeyVO":
        """Create a cache key for the loans of the member with the given filters.

        Args:
            member_id (UUID): The member identifier.
            query (MemberLoanQueryVO): The member loan query to build the key from.

        Returns:
            MemberLoanCacheKeyVO: The cache key built from the member and filters.
        """
        canonical = "|".join(
            [
                f"status={query.status.value if query.status is not None else ''}",
                f"sort_by={query.sort_by.value if query.sort_by is not None else ''}",
                f"sort_order={query.sort_order.value if query.sort_order is not None else ''}",
                f"page={query.page}",
                f"page_size={query.page_size}",
            ]
        )
        query_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        key = f"{cls._PREFIX}:{member_id}:{query_hash}"
        return cls(key=key)
