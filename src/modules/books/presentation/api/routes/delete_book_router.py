"""This module contains the delete book router."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.modules.books.application.dtos.delete_book_dto import DeleteBookCommandDto
from src.modules.books.application.use_cases.delete_book_use_case import (
    DeleteBookUseCase,
)
from src.modules.books.presentation.compositions.use_case_composition import (
    get_delete_book_use_case,
)
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.presentation.api.mappers.authenticated_user_api_mapper import (
    AuthenticatedUserApiMapper,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema
from src.shared.presentation.compositions.security_composition import get_current_user

router = APIRouter()


@router.delete(
    path="/{book_id}",
    summary="Delete a book.",
    description="This endpoint is used to delete a book. "
    "Only librarians are allowed to perform this action.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Book successfully deleted.",
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
            "description": "The book to be deleted was not found.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorsResponseSchema,
            "description": "Book delete failed.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "Invalid book delete data.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal server error.",
        },
    },
)
async def delete_book(
    book_id: UUID,
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
    use_case: DeleteBookUseCase = Depends(get_delete_book_use_case),
) -> None:
    """Delete a book.

    This endpoint is used to delete an existing book in the catalog.

    Args:
        book_id (UUID): The ID of the book to be deleted.
        current_user (AccessTokenPayloadVO): The authenticated user's access token payload.
        use_case (DeleteBookUseCase): The delete book use case.
    """
    await use_case.execute(
        DeleteBookCommandDto(book_id),
        AuthenticatedUserApiMapper.to_command(current_user.sub, current_user.role),
    )
