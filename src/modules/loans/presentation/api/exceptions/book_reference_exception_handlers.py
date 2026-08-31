"""This module contains the book reference exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.loans.domain.exceptions.book_reference_exception import (
    BookNotAvailableException,
    BookNotFoundException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def book_reference_exception_handlers(app: FastAPI) -> None:
    """Register the book reference exception handlers.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(BookNotFoundException)
    async def book_not_found_exception_handler(
        request: Request, exc: BookNotFoundException
    ) -> JSONResponse:
        """Book not found exception handler.

        Args:
            request (Request): The request object.
            exc (BookNotFoundException): The BookNotFoundException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Book not found exception occurred while processing request.",
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

    @app.exception_handler(BookNotAvailableException)
    async def book_not_available_exception_handler(
        request: Request, exc: BookNotAvailableException
    ) -> JSONResponse:
        """Book not available exception handler.

        Args:
            request (Request): The request object.
            exc (BookNotAvailableException): The BookNotAvailableException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Book not available exception occurred while processing request.",
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
