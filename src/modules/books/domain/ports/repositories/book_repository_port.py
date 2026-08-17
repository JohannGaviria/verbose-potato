"""This module contains the book repository port."""

from abc import ABC, abstractmethod

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO


class BookRepositoryPort(ABC):
    """Repository port of book entity."""

    @abstractmethod
    async def exists_by_isbn(self, isbn: IsbnVO) -> bool:
        """Check if a book exists with an ISBN.

        Args:
            isbn (IsbnVO): The isbn to check.

        Returns:
            bool: True if a book exists with an ISBN, False otherwise.
        """
        pass

    @abstractmethod
    async def save(self, entity: BookEntity) -> BookEntity:
        """Save a book entity.

        Args:
            entity (BookEntity): The book entity to be saved.

        Returns:
            BookEntity: The saved book entity.
        """
        pass
