"""This module contains the SQLAlchemy loan unit of work adapter class."""

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.books.infrastructure.persistence.repositories.sqlalchemy_book_availability_repository_adapter import (
    SQLAlchemyBookAvailabilityRepositoryAdapter,
)
from src.modules.loans.domain.ports.unit_of_work.loan_unit_of_work_port import (
    LoanUnitOfWorkPort,
)
from src.modules.loans.infrastructure.persistence.repositories.sqlalchemy_loan_repository_adapter import (
    SQLAlchemyLoanRepositoryAdapter,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.ports.outbound.logger_outbound_port import LoggerOutboundPort


class SQLAlchemyLoanUnitOfWorkAdapter(LoanUnitOfWorkPort):
    """SQLAlchemy-backed Unit of Work for loan and cross-module book operations.

    Creates a fresh :class:`AsyncSession` on entry and exposes the ``loans``
    repository and the ``book_availability`` cross-module repository bound to
    that session. On exit it rolls back automatically when an unhandled
    exception escapes the ``async with`` block; otherwise callers must
    explicitly call ``commit()``.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        logger_factory_outbound: LoggerFactoryOutboundPort,
    ) -> None:
        """Initializes the SQLAlchemyLoanUnitOfWorkAdapter.

        Args:
            session_factory (async_sessionmaker[AsyncSession]): Factory used to
                create a new session for each unit of work.
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory for
                creating loggers used by this adapter and its repositories.
        """
        self._session_factory = session_factory
        self._logger_factory = logger_factory_outbound
        self._logger: LoggerOutboundPort = logger_factory_outbound.get_logger(__name__)
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> "SQLAlchemyLoanUnitOfWorkAdapter":
        """Open a new database session and initialize the repositories.

        Returns:
            SQLAlchemyLoanUnitOfWorkAdapter: This instance, ready to use.
        """
        self._logger.debug("loan unit of work: begin transaction.")
        self._session = self._session_factory()
        self.loans = SQLAlchemyLoanRepositoryAdapter(
            session=self._session,
            logger_factory_outbound=self._logger_factory,
        )
        self.book_availability = SQLAlchemyBookAvailabilityRepositoryAdapter(
            session=self._session,
            logger_factory_outbound=self._logger_factory,
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the session, rolling back if an exception escaped the block.

        Args:
            exc_type: The exception class, if any.
            exc_val: The exception instance, if any.
            exc_tb: The traceback, if any.
        """
        if exc_type is not None:
            self._logger.warning(
                "loan unit of work: unhandled exception — rolling back.",
                exc_type=str(exc_type),
            )
            await self.rollback()

        if self._session is not None:
            await self._session.close()
            self._logger.debug("loan unit of work: session closed.")

    async def commit(self) -> None:
        """Flush and commit the current transaction.

        Raises:
            RuntimeError: If called outside an ``async with`` block.
        """
        if self._session is None:
            raise RuntimeError(
                "SQLAlchemyLoanUnitOfWorkAdapter.commit() called outside "
                "of an 'async with' block."
            )
        self._logger.debug("loan unit of work: commit.")
        await self._session.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction.

        Raises:
            RuntimeError: If called outside an ``async with`` block.
        """
        if self._session is None:
            raise RuntimeError(
                "SQLAlchemyLoanUnitOfWorkAdapter.rollback() called outside "
                "of an 'async with' block."
            )
        self._logger.debug("loan unit of work: rollback.")
        await self._session.rollback()
