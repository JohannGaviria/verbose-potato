"""This module contains the returning loan router."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.loans.application.dtos.returning_loan_dto import (
    ReturningLoanResponseDto,
)
from src.modules.loans.application.use_cases.returning_loan_use_case import (
    ReturningLoanUseCase,
)
from src.modules.loans.presentation.api.mappers.returning_loan_api_mapper import (
    ReturningLoanApiMapper,
)
from src.modules.loans.presentation.api.schemas.returning_loan_schema import (
    ReturningLoanResponseSchema,
)
from src.modules.loans.presentation.compositions.use_case_composition import (
    get_returning_loan_use_case,
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
    path="/{loan_id}/return",
    summary="Return a loan.",
    description="This endpoint is used to return a book that was previously loaned. "
    "Only members are allowed to perform this action.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[ReturningLoanResponseSchema],
            "description": "Loan returned successfully.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Authentication is required.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "The authenticated user is not a member or does not own the loan.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorsResponseSchema,
            "description": "The loan to be returned was not found.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorsResponseSchema,
            "description": "The loan has already been returned.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal server error.",
        },
    },
)
async def returning_loan(
    loan_id: UUID,
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
    use_case: ReturningLoanUseCase = Depends(get_returning_loan_use_case),
) -> JSONResponse:
    """Returning loan.

    This endpoint is used to return a previously loaned book by a member.

    Args:
        loan_id (UUID): The loan identifier to be returned.
        current_user (AccessTokenPayloadVO): The authenticated user's access token payload.
        use_case (ReturningLoanUseCase): The returning loan use case.

    Returns:
        JSONResponse: The JSON response.
    """
    response: ReturningLoanResponseDto = await use_case.execute(
        command=ReturningLoanApiMapper.to_command(loan_id),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub, role=current_user.role
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Loan returned successfully.",
                data=ReturningLoanApiMapper.to_response(response),
            )
        ),
    )
