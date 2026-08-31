"""This module contains the book availability reference value object."""

from dataclasses import dataclass
from uuid import UUID

from src.modules.loans.domain.exceptions.book_reference_exception import (
    BookNotAvailableException,
)


@dataclass(frozen=True, slots=True)
class BookAvailabilityReferenceVO:
    """Value object for book availability information.

    Attributes:
        book_id (UUID): The book id.
        available_copies (int): The available copies of the book.
    """

    book_id: UUID
    available_copies: int

    def ensure_has_available_copies(self) -> None:
        """Ensure that the book has at least one available copy.

        Raises:
            BookNotAvailableException: If the book has no available copies.
        """
        if self.available_copies <= 0:
            raise BookNotAvailableException(self.book_id)

    def reduce_available_copies(self) -> int:
        """Calculate the available copies after reducing by one.

        Returns:
            int: The new number of available copies.
        """
        self.ensure_has_available_copies()
        return self.available_copies - 1

    def increase_available_copies(self) -> int:
        """Calculate the available copies after increasing by one.

        Returns:
            int: The new number of available copies.
        """
        return self.available_copies + 1
