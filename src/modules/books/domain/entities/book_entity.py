"""This module contains the book entity."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from src.modules.books.domain.value_objects.author_vo import AuthorVO
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.domain.value_objects.published_year_vo import PublishedYearVO
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.modules.books.domain.value_objects.total_copies_vo import TotalCopiesVO
from src.shared.domain.entities.base_entity import BaseEntity


@dataclass(frozen=True, slots=True)
class BookEntity(BaseEntity):
    """Entity representing a book.

    Attributes:
        id (UUID): Unique identifier of the book.
        title (TitleVO): Title of the book.
        isbn (IsbnVO): ISBN code of the book.
        author (AuthorVO): Author of the book.
        published_year (PublishedYearVO): Year of publication.
        total_copies (TotalCopiesVO): Total number of registered copies.
        available_copies (int): Number of copies currently available.
        created_at (datetime): Record creation date.
        updated_at (datetime): Date of the last update.
    """

    title: TitleVO
    isbn: IsbnVO
    author: AuthorVO
    published_year: PublishedYearVO
    total_copies: TotalCopiesVO
    available_copies: int

    @classmethod
    def create(
        cls,
        title: TitleVO,
        isbn: IsbnVO,
        author: AuthorVO,
        published_year: PublishedYearVO,
        total_copies: TotalCopiesVO,
    ) -> "BookEntity":
        """Factory method to create a new book entity.

        Args:
            title (TitleVO): Title of the book.
            isbn (IsbnVO): ISBN code of the book.
            author (AuthorVO): Author of the book.
            published_year (PublishedYearVO): Year of publication.
            total_copies (TotalCopiesVO): Total number of registered copies.

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
            available_copies=total_copies.value,
            created_at=now,
            updated_at=now,
        )
