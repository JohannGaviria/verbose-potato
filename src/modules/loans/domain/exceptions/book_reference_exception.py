"""This module contains the book reference exceptions."""

from uuid import UUID

from src.shared.domain.exceptions.base_domain_exception import BaseDomainException


class BookNotFoundException(BaseDomainException):
    """Exception raised when a book cannot be found."""

    def __init__(self) -> None:
        """Initialize the BookNotFoundException."""
        super().__init__("Book cannot be found.")


class BookNotAvailableException(BaseDomainException):
    """Exception raised when a book not available."""

    def __init__(self, book_id: UUID) -> None:
        """Initialize the BookNotAvailableException.

        Args:
            book_id (UUID): The book id of the book to be unavailable.
        """
        self.book_id = book_id
        super().__init__("Book not available.")
