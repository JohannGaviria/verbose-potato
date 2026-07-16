"""This module contains the unit of work port class."""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self


class UnitOfWorkPort(ABC):
    """Abstract base class defining the Unit of Work contract.

    A Unit of Work tracks changes made to domain objects during a business
    transaction and coordinates the writing out of changes as a single atomic
    operation. It also acts as a context manager so callers can use it with
    ``async with`` syntax.

    Usage::

        async with unit_of_work as uow:
            user = await uow.users.save(user_entity)
            await uow.commit()
    """

    @abstractmethod
    async def __aenter__(self) -> Self:
        """Enter the unit of work context, beginning a new transaction.

        Returns:
            Self: The unit of work instance.
        """
        pass

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the unit of work context.

        If an exception occurred, the transaction is rolled back automatically.
        If the block completed without error, callers are responsible for
        calling ``commit()`` before exiting when they want changes persisted.

        Args:
            exc_type: The exception class, if any.
            exc_val: The exception instance, if any.
            exc_tb: The traceback, if any.
        """
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit all changes tracked within the current transaction.

        Raises:
            Any database-level exception propagated from the underlying adapter.
        """
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Roll back all changes tracked within the current transaction."""
        pass
