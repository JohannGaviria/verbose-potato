"""This module contains the recording loan router."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.loans.application.dtos.recording_loan_dto import (
    RecordingLoanResponseDto,
)
from src.modules.loans.application.use_cases.recording_loan_use_case import (
    RecordingLoanUseCase,
)
from src.modules.loans.presentation.api.mappers.recording_loan_api_mapper import (
    RecordingLoanApiMapper,
)
from src.modules.loans.presentation.api.schemas.recording_loan_schema import (
    RecordingLoanRequestSchema,
    RecordingLoanResponseSchema,
)
from src.modules.loans.presentation.compositions.use_case_composition import (
    get_recording_loan_use_case,
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
    path="/",
    summary="Register a loan.",
    description="This endpoint is used to register the loan of a book. "
    "Only members are allowed to perform this action.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": SuccessResponseSchema[RecordingLoanResponseSchema],
            "description": "Loan registered successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "Loan registration failed.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Authentication is required.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "The authenticated user is not a member.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorsResponseSchema,
            "description": "The book to be loaned was not found.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorsResponseSchema,
            "description": "The loan cannot be registered due to a business rule.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "Invalid loan registration data.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal server error.",
        },
    },
)
async def recording_loan(
    request: RecordingLoanRequestSchema,
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
    use_case: RecordingLoanUseCase = Depends(get_recording_loan_use_case),
) -> JSONResponse:
    """Recording loan.

    This endpoint is used to register the loan of a book by a member.

    Args:
        request (RecordingLoanRequestSchema): The recording loan request schema.
        current_user (AccessTokenPayloadVO): The authenticated user's access token payload.
        use_case (RecordingLoanUseCase): The recording loan use case.

    Returns:
        JSONResponse: The JSON response.
    """
    response: RecordingLoanResponseDto = await use_case.execute(
        command=RecordingLoanApiMapper.to_command(request),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub, role=current_user.role
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Loan registered successfully.",
                data=RecordingLoanApiMapper.to_response(response),
            )
        ),
    )
