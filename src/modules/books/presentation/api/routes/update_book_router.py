"""This module contains the update book router."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.books.application.dtos.update_book_dto import UpdateBookResponseDto
from src.modules.books.application.use_cases.update_book_use_case import (
    UpdateBookUseCase,
)
from src.modules.books.presentation.api.mappers.update_book_api_mapper import (
    UpdateBookApiMapper,
)
from src.modules.books.presentation.api.schemas.update_book_schema import (
    UpdateBookRequestSchema,
    UpdateBookResponseSchema,
)
from src.modules.books.presentation.compositions.use_case_composition import (
    get_update_book_use_case,
)
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.presentation.api.mappers.authenticated_user_api_mapper import (
    AuthenticatedUserApiMapper,
)
from src.shared.presentation.api.schemas.schema import (
    ErrorsResponseSchema,
    SuccessResponseSchema,
)
from src.shared.presentation.compositions.security_composition import get_current_user

router = APIRouter()


@router.patch(
    path="/{book_id}",
    summary="Update a book.",
    description="This endpoint is used to update an existing book in the catalog. "
    "Only the provided fields are updated. Only librarians are allowed to "
    "perform this action.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[UpdateBookResponseSchema],
            "description": "Book updated successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "Book update failed.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Authentication is required.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "The authenticated user is not a librarian.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorsResponseSchema,
            "description": "The book to be updated was not found.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "Invalid book update data.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal server error.",
        },
    },
)
async def update_book(
    book_id: UUID,
    request: UpdateBookRequestSchema,
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
    use_case: UpdateBookUseCase = Depends(get_update_book_use_case),
) -> JSONResponse:
    """Update book.

    This endpoint is used to update an existing book in the catalog.

    Args:
        book_id (UUID): The ID of the book to be updated.
        request (UpdateBookRequestSchema): The update book request schema.
        current_user (AccessTokenPayloadVO): The authenticated user's access token payload.
        use_case (UpdateBookUseCase): The update book use case.

    Returns:
        JSONResponse: The JSON response.
    """
    response: UpdateBookResponseDto = await use_case.execute(
        command=UpdateBookApiMapper.to_command(book_id, request),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub, role=current_user.role
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Book updated successfully.",
                data=UpdateBookApiMapper.to_response(response),
            )
        ),
    )
