"""This module contains the book entity."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from src.modules.books.domain.exceptions.book_exception import (
    InvalidTotalCopiesException,
)
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

    def update(
        self,
        title: TitleVO | None = None,
        author: AuthorVO | None = None,
        published_year: PublishedYearVO | None = None,
        total_copies: TotalCopiesVO | None = None,
    ) -> "BookEntity":
        """Factory method to update a book entity.

        Args:
            title (TitleVO | None): Title of the book.
            author (AuthorVO | None): Author of the book.
            published_year (PublishedYearVO | None): Year of publication.
            total_copies (TotalCopiesVO | None): Total number of registered copies.

        Returns:
            BookEntity: The updated book entity.

        Raises:
            InvalidTotalCopiesException: If the total copies cannot be less
                than currently borrowed copies.
        """
        if total_copies is not None and total_copies.value < self.available_copies:
            raise InvalidTotalCopiesException(
                "Total copies cannot be less than currently borrowed copies.",
                total_copies.value,
            )

        now = datetime.now(UTC)

        return BookEntity(
            id=self.id,
            title=title if title is not None else self.title,
            isbn=self.isbn,
            author=author if author is not None else self.author,
            published_year=published_year
            if published_year is not None
            else self.published_year,
            total_copies=total_copies
            if total_copies is not None
            else self.total_copies,
            available_copies=self.available_copies,
            created_at=self.created_at,
            updated_at=now,
        )
