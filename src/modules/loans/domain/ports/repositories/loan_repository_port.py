"""This module contains the loan repository port."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.value_objects.member_loan_query_vo import (
    MemberLoanQueryVO,
)


class LoanRepositoryPort(ABC):
    """Interface for loan repository port."""

    @abstractmethod
    async def find_by_id(self, loan_id: UUID) -> LoanEntity | None:
        """Find a loan by its identifier.

        Args:
            loan_id (UUID): Unique identifier of the loan.

        Returns:
            LoanEntity | None: The loan entity if found, otherwise None.
        """
        pass

    @abstractmethod
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
        """
        pass

    @abstractmethod
    async def exists_active_by_member_and_book(
        self, member_id: UUID, book_id: UUID
    ) -> bool:
        """Check if a loan has been active by a member and a book.

        Args:
            member_id (UUID): Member ID for the loan.
            book_id (UUID): Book ID for the loan.

        Returns:
            bool: True if the loan has been active by a member and a book, False otherwise.
        """
        pass

    @abstractmethod
    async def count_active_by_member(self, member_id: UUID) -> int:
        """Count the number of active loans by the member.

        Args:
            member_id (UUID): Member ID for the loan.

        Returns:
            int: Number of active loans by the member.
        """
        pass

    @abstractmethod
    async def save(self, entity: LoanEntity) -> LoanEntity:
        """Save a loan entity.

        Args:
            entity (LoanEntity): Loan entity to be saved.

        Returns:
            LoanEntity: Loan entity saved.
        """
        pass

    @abstractmethod
    async def update(self, entity: LoanEntity) -> LoanEntity:
        """Update a loan entity.

        Args:
            entity (LoanEntity): Loan entity to be updated.

        Returns:
            LoanEntity: Loan entity updated.
        """
        pass
