"""This module contains the loan catalog query value object."""

from dataclasses import dataclass
from uuid import UUID

from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.exceptions.loan_exception import (
    InvalidLoanCatalogQueryException,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
from src.shared.domain.value_objects.base_value_object import BaseValueObject

_MAX_PAGE_SIZE = 100


@dataclass(frozen=True, slots=True)
class LoanCatalogQueryVO(BaseValueObject):
    """Value object representing the query for the loan catalog.

    Attributes:
        member_id (UUID | None): Optional member filter for the loans.
        book_id (UUID | None): Optional book filter for the loans.
        status (LoanStatusEnum | None): Optional loan status filter.
        sort_by (LoanSortByEnum | None): Field used to sort the loans.
        sort_order (SortOrderEnum | None): Sort direction.
        page (int): The requested page number.
        page_size (int): The number of items per page.
    """

    member_id: UUID | None
    book_id: UUID | None
    status: LoanStatusEnum | None
    sort_by: LoanSortByEnum | None
    sort_order: SortOrderEnum | None
    page: int
    page_size: int

    def _validate(self) -> None:
        if self.member_id is not None and not isinstance(self.member_id, UUID):
            raise InvalidLoanCatalogQueryException(
                "member_id must be a valid UUID.", self.member_id
            )
        if self.book_id is not None and not isinstance(self.book_id, UUID):
            raise InvalidLoanCatalogQueryException(
                "book_id must be a valid UUID.", self.book_id
            )
        if self.status is not None and not isinstance(self.status, LoanStatusEnum):
            raise InvalidLoanCatalogQueryException(
                "status must be one of: 'ACTIVE', 'RETURNED'.",
                str(self.status),
            )
        if self.sort_by is not None and not isinstance(self.sort_by, LoanSortByEnum):
            raise InvalidLoanCatalogQueryException(
                "sort_by must be one of: 'loaned_at', 'returned_at'.",
                str(self.sort_by),
            )
        if self.sort_order is not None and not isinstance(
            self.sort_order, SortOrderEnum
        ):
            raise InvalidLoanCatalogQueryException(
                "sort_order must be one of: 'asc', 'desc'.", str(self.sort_order)
            )
        if isinstance(self.page, bool) or not isinstance(self.page, int):
            raise InvalidLoanCatalogQueryException(
                "page must be an integer.", self.page
            )
        if self.page < 1:
            raise InvalidLoanCatalogQueryException(
                "page must be greater than or equal to 1.", self.page
            )
        if isinstance(self.page_size, bool) or not isinstance(self.page_size, int):
            raise InvalidLoanCatalogQueryException(
                "page_size must be an integer.", self.page_size
            )
        if self.page_size < 1:
            raise InvalidLoanCatalogQueryException(
                "page_size must be greater than or equal to 1.", self.page_size
            )
        if self.page_size > _MAX_PAGE_SIZE:
            raise InvalidLoanCatalogQueryException(
                f"page_size cannot be greater than {_MAX_PAGE_SIZE}.",
                self.page_size,
            )
