"""This module contains the credentials exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidEmailException,
    InvalidNameException,
    InvalidPasswordHashException,
    InvalidPlainPasswordException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def credentials_exception_handlers(app: FastAPI) -> None:
    """Register the credentials exception handlers.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(InvalidNameException)
    async def invalid_name_exception_handler(
        request: Request, exc: InvalidNameException
    ) -> JSONResponse:
        """Invalid name exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidNameException): The InvalidNameException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid name exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            name=exc.name,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                    context={"name": exc.name},
                ),
            ),
        )

    @app.exception_handler(InvalidEmailException)
    async def invalid_email_exception_handler(
        request: Request, exc: InvalidEmailException
    ) -> JSONResponse:
        """Invalid email exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidEmailException): The InvalidEmailException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid email exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            email=exc.email,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                    context={"email": exc.email},
                ),
            ),
        )

    @app.exception_handler(InvalidPasswordHashException)
    async def invalid_password_hash_exception_handler(
        request: Request, exc: InvalidPasswordHashException
    ) -> JSONResponse:
        """Invalid password hash exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidPasswordHashException): The InvalidPasswordHashException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid password hash exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(InvalidPlainPasswordException)
    async def invalid_plain_password_exception_handler(
        request: Request, exc: InvalidPlainPasswordException
    ) -> JSONResponse:
        """Invalid plain password exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidPlainPasswordException): The InvalidPlainPasswordException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid plain password exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                ),
                exclude_none=True,
            ),
        )
