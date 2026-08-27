"""This module contains the dtos for the update book use case."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.books.domain.entities.book_entity import BookEntity


@dataclass(frozen=True, slots=True)
class UpdateBookCommandDto:
    """Command dtos for the update book use case.

    Attributes:
        book_id (UUID): The ID of the book to be updated.
        title (str | None): Title of the book.
        author (str | None): Author of the book.
        published_year (int | None): Published year of the book.
        total_copies (int | None): Total copies of the book.
    """

    book_id: UUID
    title: str | None = None
    author: str | None = None
    published_year: int | None = None
    total_copies: int | None = None


@dataclass(frozen=True, slots=True)
class UpdateBookResponseDto:
    """Response dtos for the update book use case.

    Attributes:
        id (UUID): The ID of the book.
        title (str): Title of the book.
        author (str): Author of the book.
        published_year (int): Published year of the book.
        total_copies (int): Total copies of the book.
        available_copies (int): Available copies of the book.
        created_at (datetime): Date and time the book was created.
        updated_at (datetime): Date and time the book was last updated.
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
    def response(cls, entity: BookEntity) -> "UpdateBookResponseDto":
        """Response dtos for the update book use case.

        Args:
            entity (BookEntity): The entity to be updated.

        Returns:
            UpdateBookResponseDto: The updated entity.
        """
        return cls(
            id=entity.id,
            title=entity.title.value,
            isbn=entity.isbn.value,
            author=entity.author.value,
            published_year=entity.published_year.value,
            total_copies=entity.total_copies.value,
            available_copies=entity.available_copies,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
