"""This module contains the loan exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.loans.domain.exceptions.loan_exception import (
    LoanAlreadyReturnedException,
    LoanNotFoundException,
    LoanRepositoryException,
    MaximumActiveLoansExceededException,
    MemberAlreadyHasActiveLoanException,
)
from src.modules.loans.presentation.api.exceptions.book_reference_exception_handlers import (
    book_reference_exception_handlers,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def loan_exception_handlers(app: FastAPI) -> None:
    """Register the loan exception handlers.

    Args:
        app (FastAPI): The FastAPI application.
    """
    book_reference_exception_handlers(app)

    @app.exception_handler(MemberAlreadyHasActiveLoanException)
    async def member_already_has_active_loan_exception_handler(
        request: Request, exc: MemberAlreadyHasActiveLoanException
    ) -> JSONResponse:
        """Member already has active loan exception handler.

        Args:
            request (Request): The request object.
            exc (MemberAlreadyHasActiveLoanException): The MemberAlreadyHasActiveLoanException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Member already has active loan exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(MaximumActiveLoansExceededException)
    async def maximum_active_loans_exceeded_exception_handler(
        request: Request, exc: MaximumActiveLoansExceededException
    ) -> JSONResponse:
        """Maximum active loans exceeded exception handler.

        Args:
            request (Request): The request object.
            exc (MaximumActiveLoansExceededException): The MaximumActiveLoansExceededException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Maximum active loans exceeded exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(LoanNotFoundException)
    async def loan_not_found_exception_handler(
        request: Request, exc: LoanNotFoundException
    ) -> JSONResponse:
        """Loan not found exception handler.

        Args:
            request (Request): The request object.
            exc (LoanNotFoundException): The LoanNotFoundException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Loan not found exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(LoanAlreadyReturnedException)
    async def loan_already_returned_exception_handler(
        request: Request, exc: LoanAlreadyReturnedException
    ) -> JSONResponse:
        """Loan already returned exception handler.

        Args:
            request (Request): The request object.
            exc (LoanAlreadyReturnedException): The LoanAlreadyReturnedException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Loan already returned exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(LoanRepositoryException)
    async def loan_repository_exception_handler(
        request: Request, exc: LoanRepositoryException
    ) -> JSONResponse:
        """Loan repository exception handler.

        Args:
            request (Request): The request object.
            exc (LoanRepositoryException): The LoanRepositoryException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Loan repository exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                ),
                exclude_none=True,
            ),
        )
