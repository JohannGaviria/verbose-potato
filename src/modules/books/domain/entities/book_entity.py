"""This module contains the book entity."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from src.shared.domain.entities.base_entity import BaseEntity


@dataclass(frozen=True, slots=True)
class BookEntity(BaseEntity):
    """Entity representing a book.

    Attributes:
        id (UUID): Unique identifier of the book.
        title (str): Title of the book.
        isbn (str): ISBN code of the book.
        author (str): Author of the book.
        published_year (int): Year of publication.
        total_copies (int): Total number of registered copies.
        available_copies (int): Number of copies currently available.
        created_at (datetime): Record creation date.
        updated_at (datetime): Date of the last update.
    """

    title: str  # VO
    isbn: str  # VO
    author: str  # VO
    published_year: int  # VO
    total_copies: int  # VO
    available_copies: int

    @classmethod
    def create(
        cls,
        title: str,
        isbn: str,
        author: str,
        published_year: int,
        total_copies: int,
    ) -> "BookEntity":
        """Factory method to create a new book entity.

        Args:
            title (str): Title of the book.
            isbn (str): ISBN code of the book.
            author (str): Author of the book.
            published_year (int): Year of publication.
            total_copies (int): Total number of registered copies.

        Returns:
            BookEntity: New book entity.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            title=title,
            isbn=isbn,
            author=author,
            published_year=published_year,
            total_copies=total_copies,
            available_copies=total_copies,
            created_at=now,
            updated_at=now,
        )
