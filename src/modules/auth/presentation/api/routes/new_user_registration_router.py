"""This module contains the new user registration router."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.application.dtos.new_user_registration_dto import (
    NewUserRegistrationResponseDto,
)
from src.modules.auth.application.use_cases.new_user_registration_use_case import (
    NewUserRegistrationUseCase,
)
from src.modules.auth.presentation.api.mappers.new_user_registration_api_mapper import (
    NewUserRegistrationApiMapper,
)
from src.modules.auth.presentation.api.schemas.new_user_registration_schema import (
    NewUserRegistrationRequestSchema,
    NewUserRegistrationResponseSchema,
)
from src.modules.auth.presentation.compositions.use_case_composition import (
    get_new_user_registration_use_case,
)
from src.shared.presentation.api.schemas.schema import (
    ErrorsResponseSchema,
    SuccessResponseSchema,
)

router = APIRouter()


@router.post(
    path="/register",
    summary="Register a new user.",
    description="This endpoint is used to register a new user in the system.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": SuccessResponseSchema[NewUserRegistrationResponseSchema],
            "description": "User registered successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "User registration failed.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorsResponseSchema,
            "description": "User already exists.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "Invalid user registration data.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal server error.",
        },
    },
)
async def new_user_registration(
    request: NewUserRegistrationRequestSchema,
    use_case: NewUserRegistrationUseCase = Depends(get_new_user_registration_use_case),
) -> JSONResponse:
    """New user registration.

    This endpoint is used to register a new user in the system.

    Args:
        request (NewUserRegistrationRequestSchema): The new user registration request schema.
        use_case (NewUserRegistrationUseCase): The new user registration use case.

    Returns:
        JSONResponse: The JSON response.
    """
    response: NewUserRegistrationResponseDto = await use_case.execute(
        NewUserRegistrationApiMapper.to_command(request)
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="User registered successfully.",
                data=NewUserRegistrationApiMapper.to_response(response),
            )
        ),
    )
