"""This module contains the book repository port."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO


class BookRepositoryPort(ABC):
    """Repository port of book entity."""

    @abstractmethod
    async def find_by_id(self, book_id: UUID) -> BookEntity | None:
        """Find a book by its ID.

        Args:
            book_id (UUID): The book entity to be found.

        Returns:
            BookEntity: The book entity found or None if not found.
        """
        pass

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

    @abstractmethod
    async def update(self, entity: BookEntity) -> BookEntity:
        """Update a book entity.

        Args:
            entity (BookEntity): The book entity to be updated.

        Returns:
            BookEntity: The updated book entity.
        """
        pass

    @abstractmethod
    async def delete(self, book_id: UUID) -> None:
        """Delete a book entity.

        Args:
            book_id (UUID): The book entity to be deleted.
        """
        pass
