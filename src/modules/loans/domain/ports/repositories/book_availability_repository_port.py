"""This module contains the book availability repository port."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.modules.loans.domain.value_objects.book_availability_reference_vo import (
    BookAvailabilityReferenceVO,
)


class BookAvailabilityRepositoryPort(ABC):
    """Port for accessing and modifying book availability information."""

    @abstractmethod
    async def find_by_id(self, book_id: UUID) -> BookAvailabilityReferenceVO | None:
        """Find book availability information by book identifier.

        Args:
            book_id: Unique identifier of the book.

        Returns:
            BookAvailabilityReferenceVO | None: The book availability information if
            the book exists, otherwise None.
        """
        pass

    @abstractmethod
    async def update_available_copies(
        self, book_id: UUID, available_copies: int
    ) -> None:
        """Update the number of available copies for a book.

        Args:
            book_id: Unique identifier of the book.
            available_copies: New number of available copies.

        Returns:
            None.
        """
        pass
