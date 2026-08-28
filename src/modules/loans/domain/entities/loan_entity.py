"""This module contains the loan entity."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.shared.domain.entities.base_entity import BaseEntity


@dataclass(frozen=True, slots=True)
class LoanEntity(BaseEntity):
    """Entity representing a loan.

    Attributes:
        id (UUID): Unique identifier of the loan.
        member_id (UUID): Unique identifier of the member of the loan.
        book_id (UUID): Unique identifier of the book of the loan.
        status (LoanStatusEnum): Status of the loan.
        loaned_at (datetime): Date and time at which the loan was loaned.
        returned_at (datetime): Date and time at which the loan was returned.
        created_at (datetime): Date and time at which the loan was created.
        updated_at (datetime): Date and time at which the loan was last updated.
    """

    member_id: UUID
    book_id: UUID
    status: LoanStatusEnum
    loaned_at: datetime
    returned_at: datetime | None

    @classmethod
    def create(cls, member_id: UUID, book_id: UUID) -> "LoanEntity":
        """Factory method for creating a loan entity.

        Args:
            member_id: Unique identifier of the member.
            book_id: Unique identifier of the book.

        Returns:
            LoanEntity: A newly created active loan.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            member_id=member_id,
            book_id=book_id,
            status=LoanStatusEnum.ACTIVE,
            loaned_at=now,
            returned_at=None,
            created_at=now,
            updated_at=now,
        )
