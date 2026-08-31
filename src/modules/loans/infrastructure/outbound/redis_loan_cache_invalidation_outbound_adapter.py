"""This module contains the Redis loan cache invalidation outbound adapter."""

from uuid import UUID

from src.modules.books.domain.value_objects.book_catalog_cache_key_vo import (
    BookCatalogCacheKeyVO,
)
from src.modules.books.domain.value_objects.book_catalog_cache_value_vo import (
    BookCatalogCacheValueVO,
)
from src.modules.loans.domain.ports.outbound.loan_cache_invalidation_outbound_port import (
    LoanCacheInvalidationOutboundPort,
)
from src.modules.loans.domain.value_objects.loan_catalog_cache_key_vo import (
    LoanCatalogCacheKeyVO,
)
from src.modules.loans.domain.value_objects.loan_catalog_cache_value_vo import (
    LoanCatalogCacheValueVO,
)
from src.modules.loans.domain.value_objects.member_loan_cache_key_vo import (
    MemberLoanCacheKeyVO,
)
from src.modules.loans.domain.value_objects.member_loan_cache_value_vo import (
    MemberLoanCacheValueVO,
)
from src.shared.domain.ports.outbound.cache_outbound_port import CacheOutboundPort


class RedisLoanCacheInvalidationOutboundAdapter(LoanCacheInvalidationOutboundPort):
    """Adapter used to invalidate the caches affected by loan changes from Redis."""

    def __init__(
        self,
        loan_catalog_cache_outbound: CacheOutboundPort[LoanCatalogCacheValueVO],
        member_loan_cache_outbound: CacheOutboundPort[MemberLoanCacheValueVO],
        book_catalog_cache_outbound: CacheOutboundPort[BookCatalogCacheValueVO],
    ) -> None:
        """Initialize the RedisLoanCacheInvalidationOutboundAdapter.

        Args:
            loan_catalog_cache_outbound (CacheOutboundPort[LoanCatalogCacheValueVO]): Outbound used
                to invalidate the loan catalog cache.
            member_loan_cache_outbound (CacheOutboundPort[MemberLoanCacheValueVO]): Outbound used
                to invalidate the member loan cache.
            book_catalog_cache_outbound (CacheOutboundPort[BookCatalogCacheValueVO]): Outbound used
                to invalidate the book catalog cache.
        """
        self._loan_catalog_cache_outbound = loan_catalog_cache_outbound
        self._member_loan_cache_outbound = member_loan_cache_outbound
        self._book_catalog_cache_outbound = book_catalog_cache_outbound

    async def invalidate(self, member_id: UUID) -> None:
        """Invalidate the caches affected by the loan change for the given member.

        Args:
            member_id (UUID): Identifier of the member whose loan cache must be
                invalidated.
        """
        await self._loan_catalog_cache_outbound.delete(LoanCatalogCacheKeyVO.pattern())
        await self._member_loan_cache_outbound.delete(
            MemberLoanCacheKeyVO.for_member(member_id)
        )
        await self._book_catalog_cache_outbound.delete(BookCatalogCacheKeyVO.pattern())
