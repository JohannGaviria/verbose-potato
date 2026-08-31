"""This module contains the SQLAlchemy loan repository adapter."""

from uuid import UUID

from sqlalchemy import ColumnElement, asc, desc, exists, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.exceptions.loan_exception import LoanRepositoryException
from src.modules.loans.domain.ports.repositories.loan_repository_port import (
    LoanRepositoryPort,
)
from src.modules.loans.domain.value_objects.member_loan_query_vo import (
    MemberLoanQueryVO,
)
from src.modules.loans.infrastructure.persistence.mappers.loan_persistence_mapper import (
    LoanPersistenceMapper,
)
from src.modules.loans.infrastructure.persistence.models.loan_model import LoanModel
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)

_SORT_COLUMNS = {
    LoanSortByEnum.LOANED_AT: LoanModel.loaned_at,
    LoanSortByEnum.RETURNED_AT: LoanModel.returned_at,
}


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

    async def find_by_id(self, loan_id: UUID) -> LoanEntity | None:
        """Find a loan by its identifier.

        Args:
            loan_id (UUID): Unique identifier of the loan.

        Returns:
            LoanEntity | None: The loan entity if found, otherwise None.

        Raises:
            LoanRepositoryException: If an error occurs while finding the loan.
        """
        try:
            stmt = select(LoanModel).where(LoanModel.id == loan_id)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            return LoanPersistenceMapper.to_entity(model) if model else None

        except SQLAlchemyError as exc:
            self._logger.error(
                "Error while finding loan by id.",
                error=str(exc),
            )
            raise LoanRepositoryException("Error while finding loan by id.") from exc

    async def find_by_member(
        self, member_id: UUID, query: MemberLoanQueryVO
    ) -> tuple[list[LoanEntity], int]:
        """Find the loans of the given member according to the query.

        Args:
            member_id (UUID): Member ID for the loans.
            query (MemberLoanQueryVO): The query with filters, sorting and
                pagination.

        Returns:
            tuple[list[LoanEntity], int]: The matching loan entities and the
                total number of matching loans.

        Raises:
            LoanRepositoryException: If an error occurs while finding the loans.
        """
        try:
            filters: list[ColumnElement[bool]] = [LoanModel.member_id == member_id]

            if query.status is not None:
                filters.append(LoanModel.status == query.status.value)

            count_stmt = select(func.count()).select_from(LoanModel)
            if filters:
                count_stmt = count_stmt.where(*filters)
            total_result = await self._session.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = select(LoanModel)
            if filters:
                stmt = stmt.where(*filters)

            if query.sort_by is not None:
                column = _SORT_COLUMNS[query.sort_by]
                direction = desc if query.sort_order == SortOrderEnum.DESC else asc
                stmt = stmt.order_by(direction(column))
            else:
                stmt = stmt.order_by(asc(LoanModel.loaned_at))

            stmt = stmt.offset((query.page - 1) * query.page_size).limit(
                query.page_size
            )

            result = await self._session.execute(stmt)
            models = result.scalars().all()
            loans = [LoanPersistenceMapper.to_entity(model) for model in models]

            return loans, total

        except SQLAlchemyError as exc:
            self._logger.error(
                "Error while finding loans by member.",
                error=str(exc),
            )
            raise LoanRepositoryException(
                "Error while finding loans by member."
            ) from exc

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

    async def update(self, entity: LoanEntity) -> LoanEntity:
        """Updates a LoanEntity within the current transaction and returns it.

        Args:
            entity (LoanEntity): The loan entity to be updated.

        Returns:
            LoanEntity: The updated loan entity.

        Raises:
            LoanRepositoryException: If an error occurs while updating the loan.
        """
        try:
            model = LoanPersistenceMapper.to_model(entity)
            merged_model = await self._session.merge(model)
            await self._session.flush()
            await self._session.refresh(merged_model)
            return LoanPersistenceMapper.to_entity(merged_model)

        except IntegrityError as exc:
            self._logger.error(
                "Integrity error while updating loan.", exc_info=str(exc)
            )
            raise LoanRepositoryException(
                "Loan already exists or violates constraints"
            ) from exc

        except SQLAlchemyError as exc:
            self._logger.error("Database error while updating loan.", exc_info=str(exc))
            raise LoanRepositoryException("Database error during loan update.") from exc
