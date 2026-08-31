"""This module contains the dtos for the returning loan use case."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum


@dataclass(frozen=True, slots=True)
class ReturningLoanCommandDto:
    """Command dto for the returning loan use case.

    Args:
        loan_id (UUID): Loan ID to be returned.
    """

    loan_id: UUID


@dataclass(frozen=True, slots=True)
class ReturningLoanResponseDto:
    """Response dto for the returning loan use case.

    Args:
        id (UUID): Unique ID of the loan.
        member_id (UUID): Member id of the loan.
        book_id (UUID): Book id of the loan.
        status (LoanStatusEnum): Status of the loan.
        loaned_at (datetime): Date and time of loaned date.
        returned_at (datetime | None): Date and time of returned date.
    """

    id: UUID
    member_id: UUID
    book_id: UUID
    status: LoanStatusEnum
    loaned_at: datetime
    returned_at: datetime | None

    @classmethod
    def response(cls, loan: LoanEntity) -> "ReturningLoanResponseDto":
        """Factory method to create a loan response dto.

        Args:
            loan (LoanEntity): loan entity to response.

        Returns:
            ReturningLoanResponseDto: loan response dto.
        """
        return cls(
            id=loan.id,
            member_id=loan.member_id,
            book_id=loan.book_id,
            status=loan.status,
            loaned_at=loan.loaned_at,
            returned_at=loan.returned_at,
        )
