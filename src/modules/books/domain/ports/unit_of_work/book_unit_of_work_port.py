"""This module contains the book unit of work port."""

from abc import abstractmethod

from src.modules.books.domain.ports.repositories.book_repository_port import (
    BookRepositoryPort,
)
from src.shared.domain.ports.unit_of_work.unit_of_work_port import UnitOfWorkPort


class BookUnitOfWorkPort(UnitOfWorkPort):
    """Unit of work port for book operations.

    Attributes:
        books (BookRepositoryPort): Repository used to interact with the book entity.
    """

    books: BookRepositoryPort

    @abstractmethod
    async def __aenter__(self) -> "BookUnitOfWorkPort":
        """Enter the unit of work context.

        Returns:
            BookUnitOfWorkPort: The unit of work context.
        """
        pass
