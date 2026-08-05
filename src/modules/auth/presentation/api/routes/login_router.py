"""This module contains the login router."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.application.dtos.login_dto import LoginResponseDto
from src.modules.auth.application.use_cases.login_use_case import LoginUseCase
from src.modules.auth.presentation.api.mappers.login_api_mapper import LoginApiMapper
from src.modules.auth.presentation.api.schemas.login_schema import (
    LoginRequestSchema,
    LoginResponseSchema,
)
from src.modules.auth.presentation.compositions.use_case_composition import (
    get_login_use_case,
)
from src.shared.presentation.api.schemas.schema import (
    ErrorsResponseSchema,
    SuccessResponseSchema,
)

router = APIRouter()


@router.post(
    path="/login",
    summary="Log in",
    description="Log in a user.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[LoginResponseSchema],
            "description": "Login successful.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "Login failed.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Invalid credentials.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "Invalid user login data.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal server error.",
        },
    },
)
async def login(
    request: LoginRequestSchema,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> JSONResponse:
    """Log in a user.

    This endpoint is used to log in a user in the system.

    Args:
        request (LoginRequestSchema): The login request schema.
        use_case (LoginUseCase): The login use case.

    Returns:
        JSONResponse: The JSON response.
    """
    response: LoginResponseDto = await use_case.execute(
        LoginApiMapper.to_command(request)
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Login successful.",
                data=LoginApiMapper.to_response(response),
            )
        ),
    )
