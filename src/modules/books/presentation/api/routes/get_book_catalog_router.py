"""This module contains the get book catalog router."""

from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.books.application.dtos.get_book_catalog_dto import (
    GetBookCatalogResponseDto,
)
from src.modules.books.application.use_cases.get_book_catalog_use_case import (
    GetBookCatalogUseCase,
)
from src.modules.books.domain.enums.book_catalog_sort_by_enum import (
    BookCatalogSortByEnum,
)
from src.modules.books.presentation.api.mappers.get_book_catalog_api_mapper import (
    GetBookCatalogApiMapper,
)
from src.modules.books.presentation.api.schemas.get_book_catalog_schema import (
    GetBookCatalogResponseSchema,
)
from src.modules.books.presentation.compositions.use_case_composition import (
    get_get_book_catalog_use_case,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.presentation.api.schemas.schema import (
    ErrorsResponseSchema,
    SuccessResponseSchema,
)
from src.shared.presentation.compositions.security_composition import get_current_user

router = APIRouter()


@router.get(
    path="/",
    summary="Browse the book catalog.",
    description="This endpoint is used to browse the paginated catalog of "
    "registered books. Results can be filtered by title, author, isbn, and "
    "availability, and sorted by title or published year. Any authenticated "
    "user is allowed to perform this action.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[GetBookCatalogResponseSchema],
            "description": "Book catalog retrieved successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "Invalid book catalog query.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Authentication is required.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal server error.",
        },
    },
)
async def get_book_catalog(
    title: str | None = Query(
        default=None, description="Filter books whose title contains this value."
    ),
    author: str | None = Query(
        default=None, description="Filter books whose author contains this value."
    ),
    isbn: str | None = Query(default=None, description="Filter books by exact ISBN."),
    is_available: bool | None = Query(
        default=None, description="Filter only books with available copies."
    ),
    sort_by: BookCatalogSortByEnum | None = Query(
        default=None, description="The field to sort the book catalog by."
    ),
    sort_order: SortOrderEnum | None = Query(
        default=None, description="The sort order (ascending or descending)."
    ),
    page: int = Query(default=1, description="The page number to retrieve."),
    page_size: int = Query(default=20, description="The number of items per page."),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
    use_case: GetBookCatalogUseCase = Depends(get_get_book_catalog_use_case),
) -> JSONResponse:
    """Get the book catalog.

    This endpoint is used to browse the paginated catalog of registered books.

    Args:
        title (str | None): Filter books whose title contains this value.
        author (str | None): Filter books whose author contains this value.
        isbn (str | None): Filter books by exact ISBN.
        is_available (bool | None): Filter only books with available copies.
        sort_by (BookCatalogSortByEnum | None): The field to sort the book catalog by.
        sort_order (SortOrderEnum | None): The sort order (ascending or descending).
        page (int): The page number to retrieve.
        page_size (int): The number of items per page.
        current_user (AccessTokenPayloadVO): The authenticated user's access token payload.
        use_case (GetBookCatalogUseCase): The get book catalog use case.

    Returns:
        JSONResponse: The JSON response.
    """
    response: GetBookCatalogResponseDto = await use_case.execute(
        command=GetBookCatalogApiMapper.to_command(
            title=title,
            author=author,
            isbn=isbn,
            is_available=is_available,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Book catalog retrieved successfully.",
                data=GetBookCatalogApiMapper.to_response(response),
            )
        ),
    )
