"""This module contains the SQLAlchemy loan repository adapter."""

from uuid import UUID

from sqlalchemy import exists, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.exceptions.loan_exception import LoanRepositoryException
from src.modules.loans.domain.ports.repositories.loan_repository_port import (
    LoanRepositoryPort,
)
from src.modules.loans.infrastructure.persistence.mappers.loan_persistence_mapper import (
    LoanPersistenceMapper,
)
from src.modules.loans.infrastructure.persistence.models.loan_model import LoanModel
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyLoanRepositoryAdapter(LoanRepositoryPort):
    """Adapter used to interact with the SQLAlchemy loan repository."""

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyLoanRepositoryAdapter.

        Args:
            session (AsyncSession): Database session used to interact with the database.
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
        """
        self._session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def exists_active_by_member_and_book(
        self, member_id: UUID, book_id: UUID
    ) -> bool:
        """Check if a loan has been active by a member and a book.

        Args:
            member_id (UUID): Member ID for the loan.
            book_id (UUID): Book ID for the loan.

        Returns:
            bool: True if the loan has been active by a member and a book, False otherwise.

        Raises:
            LoanRepositoryException: If an error occurs while checking the loan.
        """
        try:
            stmt = select(
                exists().where(
                    LoanModel.member_id == member_id,
                    LoanModel.book_id == book_id,
                    LoanModel.status == LoanStatusEnum.ACTIVE.value,
                )
            )
            result = await self._session.execute(stmt)
            return result.scalar_one()

        except SQLAlchemyError as exc:
            self._logger.error(
                "Error while checking if an active loan exists by member and book.",
                error=str(exc),
            )
            raise LoanRepositoryException(
                "Error while checking if an active loan exists by member and book."
            ) from exc

    async def count_active_by_member(self, member_id: UUID) -> int:
        """Count the number of active loans by the member.

        Args:
            member_id (UUID): Member ID for the loan.

        Returns:
            int: Number of active loans by the member.

        Raises:
            LoanRepositoryException: If an error occurs while counting the loans.
        """
        try:
            stmt = (
                select(func.count())
                .select_from(LoanModel)
                .where(
                    LoanModel.member_id == member_id,
                    LoanModel.status == LoanStatusEnum.ACTIVE.value,
                )
            )
            result = await self._session.execute(stmt)
            return result.scalar_one()

        except SQLAlchemyError as exc:
            self._logger.error(
                "Error while counting active loans by member.",
                error=str(exc),
            )
            raise LoanRepositoryException(
                "Error while counting active loans by member."
            ) from exc

    async def save(self, entity: LoanEntity) -> LoanEntity:
        """Persists a LoanEntity within the current transaction and returns it.

        Args:
            entity (LoanEntity): The loan entity to be saved.

        Returns:
            LoanEntity: The saved loan entity.

        Raises:
            LoanRepositoryException: If an error occurs while saving the loan.
        """
        try:
            model = LoanPersistenceMapper.to_model(entity)
            self._session.add(model)
            await self._session.flush()
            await self._session.refresh(model)
            return LoanPersistenceMapper.to_entity(model)

        except IntegrityError as exc:
            self._logger.error("Integrity error while saving loan.", exc_info=str(exc))
            raise LoanRepositoryException(
                "Loan already exists or violates constraints"
            ) from exc

        except SQLAlchemyError as exc:
            self._logger.error("Database error while saving loan.", exc_info=str(exc))
            raise LoanRepositoryException(
                "Database error during loan creation."
            ) from exc
