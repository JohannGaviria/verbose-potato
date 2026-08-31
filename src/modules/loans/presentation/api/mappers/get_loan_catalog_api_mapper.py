"""This module contains the get loan catalog api mapper class."""

from uuid import UUID

from src.modules.loans.application.dtos.get_loan_catalog_dto import (
    GetLoanCatalogCommandDto,
    GetLoanCatalogItemResponseDto,
    GetLoanCatalogResponseDto,
)
from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.presentation.api.schemas.get_loan_catalog_schema import (
    GetLoanCatalogItemResponseSchema,
    GetLoanCatalogResponseSchema,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum


class GetLoanCatalogApiMapper:
    """Mapper class for the get loan catalog API."""

    @staticmethod
    def to_command(
        member_id: UUID | None,
        book_id: UUID | None,
        status: LoanStatusEnum | None,
        sort_by: LoanSortByEnum | None,
        sort_order: SortOrderEnum | None,
        page: int,
        page_size: int,
    ) -> GetLoanCatalogCommandDto:
        """Maps the get loan catalog query parameters to a command DTO.

        Args:
            member_id (UUID | None): The member filter for the loans.
            book_id (UUID | None): The book filter for the loans.
            status (LoanStatusEnum | None): The loan status filter.
            sort_by (LoanSortByEnum | None): The field to sort the loans by.
            sort_order (SortOrderEnum | None): The sort order.
            page (int): The page of the loan catalog.
            page_size (int): The page size of the loan catalog.

        Returns:
            GetLoanCatalogCommandDto: The get loan catalog command DTO.
        """
        return GetLoanCatalogCommandDto(
            member_id=member_id,
            book_id=book_id,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    def to_response(
        response: GetLoanCatalogResponseDto,
    ) -> GetLoanCatalogResponseSchema:
        """Maps a get loan catalog response DTO to a response schema.

        Args:
            response (GetLoanCatalogResponseDto): The get loan catalog response DTO.

        Returns:
            GetLoanCatalogResponseSchema: The get loan catalog response schema.
        """
        return GetLoanCatalogResponseSchema(
            items=[
                GetLoanCatalogApiMapper._to_item_response(item)
                for item in response.items
            ],
            total=response.total,
            page=response.page,
            page_size=response.page_size,
            total_pages=response.total_pages,
        )

    @staticmethod
    def _to_item_response(
        item: GetLoanCatalogItemResponseDto,
    ) -> GetLoanCatalogItemResponseSchema:
        """Maps a get loan catalog item response DTO to an item response schema.

        Args:
            item (GetLoanCatalogItemResponseDto): The get loan catalog item response DTO.

        Returns:
            GetLoanCatalogItemResponseSchema: The get loan catalog item response schema.
        """
        return GetLoanCatalogItemResponseSchema(
            id=item.id,
            member_id=item.member_id,
            book_id=item.book_id,
            status=item.status,
            loaned_at=item.loaned_at,
            returned_at=item.returned_at,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
