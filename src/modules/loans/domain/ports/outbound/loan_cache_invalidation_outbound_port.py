"""This module contains the loan cache invalidation outbound port."""

from abc import ABC, abstractmethod
from uuid import UUID


class LoanCacheInvalidationOutboundPort(ABC):
    """Port for invalidating caches affected by loan changes."""

    @abstractmethod
    async def invalidate(self, member_id: UUID) -> None:
        """Invalidate caches affected by a loan change.

        Args:
            member_id (UUID): Identifier of the member whose loan cache must be
                invalidated.
        """
        pass
