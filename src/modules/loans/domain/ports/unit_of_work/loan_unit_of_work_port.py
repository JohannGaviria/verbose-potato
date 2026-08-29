"""This module contains the loan unit of work port."""

from abc import abstractmethod

from src.modules.loans.domain.ports.repositories.book_availability_repository_port import (
    BookAvailabilityRepositoryPort,
)
from src.modules.loans.domain.ports.repositories.loan_repository_port import (
    LoanRepositoryPort,
)
from src.shared.domain.ports.unit_of_work.unit_of_work_port import UnitOfWorkPort


class LoanUnitOfWorkPort(UnitOfWorkPort):
    """Unit of work port for loan operation and book cross-module operation.

    Attributes:
        loans (LoanRepositoryPort): Repository used to interact with the loans.
        book_availability (BooksAvailabilityRepositoryPort): Repository used to interact with
            the books availability cross-module.
    """

    loans: LoanRepositoryPort
    book_availability: BookAvailabilityRepositoryPort

    @abstractmethod
    async def __aenter__(self) -> "LoanUnitOfWorkPort":
        """Enter the unit of work context.

        Returns:
            LoanUnitOfWorkPort: The unit of work context.
        """
        pass
