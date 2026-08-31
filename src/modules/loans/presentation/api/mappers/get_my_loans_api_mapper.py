"""This module contains the get my loans api mapper class."""

from src.modules.loans.application.dtos.get_my_loans_dto import (
    GetMyLoansCommandDto,
    GetMyLoansItemResponseDto,
    GetMyLoansResponseDto,
)
from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.presentation.api.schemas.get_my_loans_schema import (
    GetMyLoansItemResponseSchema,
    GetMyLoansResponseSchema,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum


class GetMyLoansApiMapper:
    """Mapper class for the get my loans API."""

    @staticmethod
    def to_command(
        status: LoanStatusEnum | None,
        sort_by: LoanSortByEnum | None,
        sort_order: SortOrderEnum | None,
        page: int,
        page_size: int,
    ) -> GetMyLoansCommandDto:
        """Maps the get my loans query parameters to a command DTO.

        Args:
            status (LoanStatusEnum | None): The loan status filter.
            sort_by (LoanSortByEnum | None): The field to sort the loans by.
            sort_order (SortOrderEnum | None): The sort order.
            page (int): The page of the member loans.
            page_size (int): The page size of the member loans.

        Returns:
            GetMyLoansCommandDto: The get my loans command DTO.
        """
        return GetMyLoansCommandDto(
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    def to_response(
        response: GetMyLoansResponseDto,
    ) -> GetMyLoansResponseSchema:
        """Maps a get my loans response DTO to a response schema.

        Args:
            response (GetMyLoansResponseDto): The get my loans response DTO.

        Returns:
            GetMyLoansResponseSchema: The get my loans response schema.
        """
        return GetMyLoansResponseSchema(
            items=[
                GetMyLoansApiMapper._to_item_response(item) for item in response.items
            ],
            total=response.total,
            page=response.page,
            page_size=response.page_size,
            total_pages=response.total_pages,
        )

    @staticmethod
    def _to_item_response(
        item: GetMyLoansItemResponseDto,
    ) -> GetMyLoansItemResponseSchema:
        """Maps a get my loans item response DTO to an item response schema.

        Args:
            item (GetMyLoansItemResponseDto): The get my loans item response DTO.

        Returns:
            GetMyLoansItemResponseSchema: The get my loans item response schema.
        """
        return GetMyLoansItemResponseSchema(
            id=item.id,
            member_id=item.member_id,
            book_id=item.book_id,
            status=item.status,
            loaned_at=item.loaned_at,
            returned_at=item.returned_at,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
