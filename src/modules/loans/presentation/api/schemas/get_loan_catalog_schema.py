"""This module contains the get loan catalog schema."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum


class GetLoanCatalogItemResponseSchema(BaseModel):
    """Response schema for a single loan within the loan catalog.

    Attributes:
        id (UUID): The loan's id.
        member_id (UUID): The member's id.
        book_id (UUID): The book's id.
        status (LoanStatusEnum): The loan's status.
        loaned_at (datetime): The date and time of the loan.
        returned_at (datetime | None): The date and time of the return.
        created_at (datetime): The loan's creation date.
        updated_at (datetime): The loan's update date.
    """

    id: UUID
    member_id: UUID
    book_id: UUID
    status: LoanStatusEnum
    loaned_at: datetime
    returned_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "7e707d97-5896-4ad2-945d-f29e9e61ddc7",
                "member_id": "2e707d97-5896-4ad2-945d-f29e9e61ddc7",
                "book_id": "3e707d97-5896-4ad2-945d-f29e9e61ddc7",
                "status": "ACTIVE",
                "loaned_at": "2026-08-30 18:59:40.152699+00:00",
                "returned_at": None,
                "created_at": "2026-08-30 18:59:40.152699+00:00",
                "updated_at": "2026-08-30 18:59:40.152699+00:00",
            }
        }
    }


class GetLoanCatalogResponseSchema(BaseModel):
    """Response schema for the paginated loan catalog.

    Attributes:
        items (list[GetLoanCatalogItemResponseSchema]): The loans for the current page.
        total (int): The total number of loans matching the filters, ignoring pagination.
        page (int): The current page number.
        page_size (int): The number of items per page.
        total_pages (int): The total number of pages available.
    """

    items: list[GetLoanCatalogItemResponseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": "7e707d97-5896-4ad2-945d-f29e9e61ddc7",
                        "member_id": "2e707d97-5896-4ad2-945d-f29e9e61ddc7",
                        "book_id": "3e707d97-5896-4ad2-945d-f29e9e61ddc7",
                        "status": "ACTIVE",
                        "loaned_at": "2026-08-30 18:59:40.152699+00:00",
                        "returned_at": None,
                        "created_at": "2026-08-30 18:59:40.152699+00:00",
                        "updated_at": "2026-08-30 18:59:40.152699+00:00",
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 20,
                "total_pages": 1,
            }
        }
    }
