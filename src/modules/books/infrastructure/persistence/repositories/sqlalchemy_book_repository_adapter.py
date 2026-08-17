"""This module contains the SQLAlchemy book repository adapter."""

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
