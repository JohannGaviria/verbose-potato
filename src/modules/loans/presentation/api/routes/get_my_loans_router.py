"""This module contains the get my loans router."""

from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.loans.application.dtos.get_my_loans_dto import (
    GetMyLoansResponseDto,
)
from src.modules.loans.application.use_cases.get_my_loans_use_case import (
    GetMyLoansUseCase,
)
from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.presentation.api.mappers.get_my_loans_api_mapper import (
    GetMyLoansApiMapper,
)
from src.modules.loans.presentation.api.schemas.get_my_loans_schema import (
    GetMyLoansResponseSchema,
)
from src.modules.loans.presentation.compositions.use_case_composition import (
    get_get_my_loans_use_case,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
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


@router.get(
    path="/me",
    summary="Get the loans of the authenticated member.",
    description="This endpoint is used to retrieve the paginated loans of the "
    "authenticated member. Results can be filtered by status and sorted by loaned "
    "date or returned date. Only members are allowed to perform this action.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[GetMyLoansResponseSchema],
            "description": "Member loans retrieved successfully.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Authentication is required.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "The authenticated user is not a member.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal server error.",
        },
    },
)
async def get_my_loans(
    status_filter: LoanStatusEnum | None = Query(
        default=None, alias="status", description="Filter loans by status."
    ),
    sort_by: LoanSortByEnum | None = Query(
        default=None, description="The field to sort the loans by."
    ),
    sort_order: SortOrderEnum | None = Query(
        default=None, description="The sort order (ascending or descending)."
    ),
    page: int = Query(default=1, ge=1, description="The page number to retrieve."),
    page_size: int = Query(
        default=20, ge=1, le=100, description="The number of items per page."
    ),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
    use_case: GetMyLoansUseCase = Depends(get_get_my_loans_use_case),
) -> JSONResponse:
    """Get the loans of the authenticated member.

    This endpoint is used to retrieve the paginated loans of the authenticated member.

    Args:
        status_filter (LoanStatusEnum | None): Filter loans by status.
        sort_by (LoanSortByEnum | None): The field to sort the loans by.
        sort_order (SortOrderEnum | None): The sort order.
        page (int): The page number to retrieve.
        page_size (int): The number of items per page.
        current_user (AccessTokenPayloadVO): The authenticated user's access token payload.
        use_case (GetMyLoansUseCase): The get my loans use case.

    Returns:
        JSONResponse: The JSON response.
    """
    response: GetMyLoansResponseDto = await use_case.execute(
        command=GetMyLoansApiMapper.to_command(
            status=status_filter,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        ),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub, role=current_user.role
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Member loans retrieved successfully.",
                data=GetMyLoansApiMapper.to_response(response),
            )
        ),
    )
