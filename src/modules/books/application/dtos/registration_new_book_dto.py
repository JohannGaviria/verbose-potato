"""This module contains the dtos for the registration new book use case."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.books.domain.entities.book_entity import BookEntity


@dataclass(frozen=True, slots=True)
class RegistrationNewBookCommandDto:
    """Command DTO for the registration new book use case.

    Attributes:
        title (str): The title of the book.
        isbn (str): The ISBN of the book.
        author (str): The author of the book.
        published_year (int): The year of publication of the book.
        total_copies (int): The total number of copies of the book.
    """

    title: str
    isbn: str
    author: str
    published_year: int
    total_copies: int


@dataclass(frozen=True, slots=True)
class RegistrationNewBookResponseDto:
    """Response DTO for the registration new book use case.

    Attributes:
        id (UUID): The unique identifier of the book.
        title (str): The title of the book.
        isbn (str): The ISBN of the book.
        author (str): The author of the book.
        published_year (int): The year of publication of the book.
        total_copies (int): The total number of copies of the book.
        available_copies (int): The number of available copies of the book.
        created_at (datetime): The date and time when the book was created.
        updated_at (datetime): The date and time when the book was last updated.
    """

    id: UUID
    title: str
    isbn: str
    author: str
    published_year: int
    total_copies: int
    available_copies: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def response(cls, book: BookEntity) -> "RegistrationNewBookResponseDto":
        """Factory method for the response DTO.

        Args:
            book (BookEntity): The book to be converted to a response DTO.

        Returns:
            RegistrationNewBookResponseDto: The new instance of the response DTO.
        """
        return cls(
            id=book.id,
            title=book.title.value,
            isbn=book.isbn.value,
            author=book.author.value,
            published_year=book.published_year.value,
            total_copies=book.total_copies.value,
            available_copies=book.available_copies,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )
