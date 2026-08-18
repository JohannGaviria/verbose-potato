"""This module contains the SQLAlchemy book repository adapter."""

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.exceptions.book_exception import BookRepositoryException
from src.modules.books.domain.ports.repositories.book_repository_port import (
    BookRepositoryPort,
)
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.infrastructure.persistence.mappers.book_persistence_mapper import (
    BookPersistenceMapper,
)
from src.modules.books.infrastructure.persistence.models.book_model import BookModel
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyBookRepositoryAdapter(BookRepositoryPort):
    """Adapter used to interact with the SQLAlchemy book repository."""

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyBookRepositoryAdapter.

        Args:
            session (AsyncSession): Database session used to interact with the database.
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
        """
        self._session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def find_by_id(self, book_id: UUID) -> BookEntity | None:
        """Find a book by its ID.

        Args:
            book_id (UUID): The book entity to be found.

        Returns:
            BookEntity | None: The book entity found or None if not found.

        Raises:
            BookRepositoryException: If an error occurs while finding the book.
        """
        try:
            stmt = select(BookModel).where(BookModel.id == book_id)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            return BookPersistenceMapper.to_entity(model) if model else None

        except SQLAlchemyError as exc:
            self._logger.error(
                "Error while finding book by id.",
                error=str(exc),
            )
            raise BookRepositoryException("Error while finding book by id.") from exc

    async def exists_by_isbn(self, isbn: IsbnVO) -> bool:
        """Check if a book exists with an ISBN.

        Args:
            isbn (IsbnVO): The isbn to check.

        Returns:
            bool: True if a book exists with an ISBN, False otherwise.

        Raises:
            BookRepositoryException: If an error occurs while checking if a book exists.
        """
        try:
            stmt = select(exists().where(BookModel.isbn == isbn.value))
            result = await self._session.execute(stmt)
            return result.scalar_one()

        except SQLAlchemyError as exc:
            self._logger.error(
                "Error while checking if a book exists by isbn.",
                error=str(exc),
            )
            raise BookRepositoryException(
                "Error while checking if a book exists by isbn."
            ) from exc

    async def save(self, entity: BookEntity) -> BookEntity:
        """Persists a BookEntity within the current transaction and returns it.

        Args:
            entity (BookEntity): The book entity to be saved.

        Returns:
            BookEntity: The saved book entity.

        Raises:
            BookRepositoryException: If an error occurs while saving the book.
        """
        try:
            model = BookPersistenceMapper.to_model(entity)
            self._session.add(model)
            await self._session.flush()
            await self._session.refresh(model)
            return BookPersistenceMapper.to_entity(model)

        except IntegrityError as exc:
            self._logger.error("Integrity error while saving book", exc_info=str(exc))
            raise BookRepositoryException(
                "Book already exists or violates constraints"
            ) from exc

        except SQLAlchemyError as exc:
            self._logger.error("Database error while saving book", exc_info=str(exc))
            raise BookRepositoryException(
                "Database error during book creation."
            ) from exc

    async def update(self, entity: BookEntity) -> BookEntity:
        """Updates a BookEntity within the current transaction and returns it.

        Args:
            entity (BookEntity): The book entity to be updated.

        Returns:
            BookEntity: The updated book entity.

        Raises:
            BookRepositoryException: If an error occurs while updating the book.
        """
        try:
            model = BookPersistenceMapper.to_model(entity)
            merged_model = await self._session.merge(model)
            await self._session.flush()
            await self._session.refresh(merged_model)
            return BookPersistenceMapper.to_entity(merged_model)

        except IntegrityError as exc:
            self._logger.error("Integrity error while updating book", exc_info=str(exc))
            raise BookRepositoryException(
                "Book already exists or violates constraints"
            ) from exc

        except SQLAlchemyError as exc:
            self._logger.error("Database error while updating book", exc_info=str(exc))
            raise BookRepositoryException("Database error during book update.") from exc
