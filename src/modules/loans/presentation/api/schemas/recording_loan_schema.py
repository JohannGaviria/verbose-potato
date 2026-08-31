"""This module contains the recording loan schema."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum


class RecordingLoanRequestSchema(BaseModel):
    """Request schema for recording loan.

    Attributes:
        book_id (UUID): The identifier of the book to loan.
    """

    book_id: UUID

    model_config = {
        "json_schema_extra": {
            "example": {
                "book_id": "7e707d97-5896-4ad2-945d-f29e9e61ddc7",
            }
        }
    }


class RecordingLoanResponseSchema(BaseModel):
    """Response schema for recording loan.

    Attributes:
        id (UUID): The loan's id.
        member_id (UUID): The member's id.
        book_id (UUID): The book's id.
        status (LoanStatusEnum): The loan's status.
        loaned_at (datetime): The date and time of the loan.
        returned_at (datetime | None): The date and time of the return.
    """

    id: UUID
    member_id: UUID
    book_id: UUID
    status: LoanStatusEnum
    loaned_at: datetime
    returned_at: datetime | None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "7e707d97-5896-4ad2-945d-f29e9e61ddc7",
                "member_id": "2e707d97-5896-4ad2-945d-f29e9e61ddc7",
                "book_id": "3e707d97-5896-4ad2-945d-f29e9e61ddc7",
                "status": "ACTIVE",
                "loaned_at": "2026-08-30 18:59:40.152699+00:00",
                "returned_at": None,
            }
        }
    }
