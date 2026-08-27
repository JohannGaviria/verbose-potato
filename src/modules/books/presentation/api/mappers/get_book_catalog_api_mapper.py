"""This module contains the get book catalog api mapper class."""

from src.modules.books.application.dtos.get_book_catalog_dto import (
    GetBookCatalogCommandDto,
    GetBookCatalogItemResponseDto,
    GetBookCatalogResponseDto,
)
from src.modules.books.domain.enums.book_catalog_sort_by_enum import (
    BookCatalogSortByEnum,
)
from src.modules.books.presentation.api.schemas.get_book_catalog_schema import (
    GetBookCatalogItemResponseSchema,
    GetBookCatalogResponseSchema,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum


class GetBookCatalogApiMapper:
    """Mapper class for the get book catalog API."""

    @staticmethod
    def to_command(
        title: str | None,
        author: str | None,
        isbn: str | None,
        is_available: bool | None,
        sort_by: BookCatalogSortByEnum | None,
        sort_order: SortOrderEnum | None,
        page: int,
        page_size: int,
    ) -> GetBookCatalogCommandDto:
        """Maps the get book catalog query parameters to a command DTO.

        Args:
            title (str | None): The title filter for the book catalog.
            author (str | None): The author filter for the book catalog.
            isbn (str | None): The ISBN filter for the book catalog.
            is_available (bool | None): Whether to filter only available books.
            sort_by (BookCatalogSortByEnum | None): The field to sort the book catalog by.
            sort_order (SortOrderEnum | None): The sort order.
            page (int): The page of the book catalog.
            page_size (int): The page size of the book catalog.

        Returns:
            GetBookCatalogCommandDto: The get book catalog command DTO.
        """
        return GetBookCatalogCommandDto(
            title=title,
            author=author,
            isbn=isbn,
            is_available=is_available,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    def to_response(
        response: GetBookCatalogResponseDto,
    ) -> GetBookCatalogResponseSchema:
        """Maps a get book catalog response DTO to a response schema.

        Args:
            response (GetBookCatalogResponseDto): The get book catalog response DTO.

        Returns:
            GetBookCatalogResponseSchema: The get book catalog response schema.
        """
        return GetBookCatalogResponseSchema(
            items=[
                GetBookCatalogApiMapper._to_item_response(item)
                for item in response.items
            ],
            total=response.total,
            page=response.page,
            page_size=response.page_size,
            total_pages=response.total_pages,
        )

    @staticmethod
    def _to_item_response(
        item: GetBookCatalogItemResponseDto,
    ) -> GetBookCatalogItemResponseSchema:
        """Maps a get book catalog item response DTO to an item response schema.

        Args:
            item (GetBookCatalogItemResponseDto): The get book catalog item response DTO.

        Returns:
            GetBookCatalogItemResponseSchema: The get book catalog item response schema.
        """
        return GetBookCatalogItemResponseSchema(
            id=item.id,
            title=item.title,
            isbn=item.isbn,
            author=item.author,
            published_year=item.published_year,
            total_copies=item.total_copies,
            available_copies=item.available_copies,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
