"""This module contains the SQLAlchemy book availability repository adapter."""

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.books.domain.exceptions.book_exception import BookRepositoryException
from src.modules.books.infrastructure.persistence.models.book_model import BookModel
from src.modules.loans.domain.ports.repositories.book_availability_repository_port import (
    BookAvailabilityRepositoryPort,
)
from src.modules.loans.domain.value_objects.book_availability_reference_vo import (
    BookAvailabilityReferenceVO,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyBookAvailabilityRepositoryAdapter(BookAvailabilityRepositoryPort):
    """Adapter used to interact with the SQLAlchemy book availability repository."""

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyBookAvailabilityRepositoryAdapter.

        Args:
            session (AsyncSession): Database session used to interact with the database.
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
        """
        self._session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def find_by_id(self, book_id: UUID) -> BookAvailabilityReferenceVO | None:
        """Find book availability information by book identifier.

        Args:
            book_id (UUID): Unique identifier of the book.

        Returns:
            BookAvailabilityReferenceVO | None: The book availability information if
            the book exists, otherwise None.

        Raises:
            BookRepositoryException: If an error occurs while finding the book
                availability.
        """
        try:
            stmt = select(BookModel).where(BookModel.id == book_id)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return BookAvailabilityReferenceVO(
                book_id=model.id,
                available_copies=model.available_copies,
            )

        except SQLAlchemyError as exc:
            self._logger.error(
                "Error while finding book availability by id.",
                error=str(exc),
            )
            raise BookRepositoryException(
                "Error while finding book availability by id."
            ) from exc

    async def update_available_copies(
        self, book_id: UUID, available_copies: int
    ) -> None:
        """Update the number of available copies for a book.

        Args:
            book_id (UUID): Unique identifier of the book.
            available_copies (int): New number of available copies.

        Raises:
            BookRepositoryException: If an error occurs while updating the book
                availability.
        """
        try:
            stmt = (
                update(BookModel)
                .where(BookModel.id == book_id)
                .values(available_copies=available_copies)
            )
            await self._session.execute(stmt)
            await self._session.flush()

        except SQLAlchemyError as exc:
            self._logger.error(
                "Error while updating book available copies.",
                error=str(exc),
            )
            raise BookRepositoryException(
                "Error while updating book available copies."
            ) from exc
