"""This module contains the member loan cache key value object."""

from dataclasses import dataclass
from uuid import UUID

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
