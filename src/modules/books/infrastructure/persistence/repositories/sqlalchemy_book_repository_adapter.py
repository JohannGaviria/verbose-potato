"""This module contains the SQLAlchemy book repository adapter."""

from uuid import UUID

from sqlalchemy import ColumnElement, asc, delete, desc, exists, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.enums.book_catalog_sort_by_enum import (
    BookCatalogSortByEnum,
)
from src.modules.books.domain.exceptions.book_exception import BookRepositoryException
from src.modules.books.domain.ports.repositories.book_repository_port import (
    BookRepositoryPort,
)
from src.modules.books.domain.value_objects.book_catalog_query_vo import (
    BookCatalogQueryVO,
)
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.infrastructure.persistence.mappers.book_persistence_mapper import (
    BookPersistenceMapper,
)
from src.modules.books.infrastructure.persistence.models.book_model import BookModel
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)

_SORT_COLUMNS = {
    BookCatalogSortByEnum.TITLE: BookModel.title,
    BookCatalogSortByEnum.PUBLISHED_YEAR: BookModel.published_year,
}


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

    async def find_catalog(
        self, query: BookCatalogQueryVO
    ) -> tuple[list[BookEntity], int]:
        """Find books matching the specified catalog query.

        Args:
            query: Query parameters containing filters, sorting, and pagination
                criteria.

        Returns:
            tuple[list[BookEntity], int]: A tuple containing the books for the requested page and
            the total number of books matching the query filters.

        Raises:
            BookRepositoryException: If an error occurs while finding the book catalog.
        """
        try:
            filters: list[ColumnElement[bool]] = []

            if query.title is not None:
                filters.append(BookModel.title.ilike(f"%{query.title.value}%"))
            if query.author is not None:
                filters.append(BookModel.author.ilike(f"%{query.author.value}%"))
            if query.isbn is not None:
                filters.append(BookModel.isbn == query.isbn.value)
            if query.is_available:
                filters.append(BookModel.available_copies > 0)

            count_stmt = select(func.count()).select_from(BookModel)
            if filters:
                count_stmt = count_stmt.where(*filters)
            total_result = await self._session.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = select(BookModel)
            if filters:
                stmt = stmt.where(*filters)

            if query.sort_by is not None:
                column = _SORT_COLUMNS[query.sort_by]
                direction = desc if query.sort_order == SortOrderEnum.DESC else asc
                stmt = stmt.order_by(direction(column))
            else:
                stmt = stmt.order_by(asc(BookModel.created_at))

            stmt = stmt.offset((query.page - 1) * query.page_size).limit(
                query.page_size
            )

            result = await self._session.execute(stmt)
            models = result.scalars().all()
            books = [BookPersistenceMapper.to_entity(model) for model in models]

            return books, total

        except SQLAlchemyError as exc:
            self._logger.error(
                "Error while finding the book catalog.",
                error=str(exc),
            )
            raise BookRepositoryException(
                "Error while finding the book catalog."
            ) from exc

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
            self._logger.error("Integrity error while saving book.", exc_info=str(exc))
            raise BookRepositoryException(
                "Book already exists or violates constraints"
            ) from exc

        except SQLAlchemyError as exc:
            self._logger.error("Database error while saving book.", exc_info=str(exc))
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
            self._logger.error(
                "Integrity error while updating book.", exc_info=str(exc)
            )
            raise BookRepositoryException(
                "Book already exists or violates constraints"
            ) from exc

        except SQLAlchemyError as exc:
            self._logger.error("Database error while updating book.", exc_info=str(exc))
            raise BookRepositoryException("Database error during book update.") from exc

    async def delete(self, book_id: UUID) -> None:
        """Deletes a book entity within the current transaction.

        Args:
            book_id (UUID): The book entity to be deleted.

        Raises:
            BookRepositoryException: If an error occurs while deleting the book.
        """
        try:
            stmt = delete(BookModel).where(BookModel.id == book_id)
            await self._session.execute(stmt)
            await self._session.flush()

        except SQLAlchemyError as exc:
            self._logger.error("Database error while deleting book.", exc_info=str(exc))
            raise BookRepositoryException(
                "Database error during book deletion."
            ) from exc
