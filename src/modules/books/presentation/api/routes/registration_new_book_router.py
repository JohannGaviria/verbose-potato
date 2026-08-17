"""This module contains the registration new book router."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.books.application.dtos.registration_new_book_dto import (
    RegistrationNewBookResponseDto,
)
from src.modules.books.application.use_cases.registration_new_book_use_case import (
    RegistrationNewBookUseCase,
)
from src.modules.books.presentation.api.mappers.registration_new_book_api_mapper import (
    RegistrationNewBookApiMapper,
)
from src.modules.books.presentation.api.schemas.registration_new_book_schema import (
    RegistrationNewBookRequestSchema,
    RegistrationNewBookResponseSchema,
)
from src.modules.books.presentation.compositions.use_case_composition import (
    get_registration_new_book_use_case,
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


@router.post(
    path="/register",
    summary="Register a new book.",
    description="This endpoint is used to register a new book in the catalog. "
    "Only librarians are allowed to perform this action.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": SuccessResponseSchema[RegistrationNewBookResponseSchema],
            "description": "Book registered successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "Book registration failed.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Authentication is required.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "The authenticated user is not a librarian.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorsResponseSchema,
            "description": "A book with this ISBN is already registered.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "Invalid book registration data.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal server error.",
        },
    },
)
async def registration_new_book(
    request: RegistrationNewBookRequestSchema,
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
    use_case: RegistrationNewBookUseCase = Depends(get_registration_new_book_use_case),
) -> JSONResponse:
    """Registration new book.

    This endpoint is used to register a new book in the catalog.

    Args:
        request (RegistrationNewBookRequestSchema): The registration new book request schema.
        current_user (AccessTokenPayloadVO): The authenticated user's access token payload.
        use_case (RegistrationNewBookUseCase): The registration new book use case.

    Returns:
        JSONResponse: The JSON response.
    """
    response: RegistrationNewBookResponseDto = await use_case.execute(
        command=RegistrationNewBookApiMapper.to_command(request),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub, role=current_user.role
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Book registered successfully.",
                data=RegistrationNewBookApiMapper.to_response(response),
            )
        ),
    )
