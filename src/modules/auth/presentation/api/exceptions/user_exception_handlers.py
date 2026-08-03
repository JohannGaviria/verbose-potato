"""This module contains the user exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.domain.exceptions.user_exception import (
    LibrarianAlreadyExistsException,
    UserAlreadyExistsException,
    UserRepositoryException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def user_exception_handlers(app: FastAPI) -> None:
    """Register the user exception handlers.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(UserAlreadyExistsException)
    async def user_already_exists_exception_handler(
        request: Request, exc: UserAlreadyExistsException
    ) -> JSONResponse:
        """User already exists exception handler.

        Args:
            request (Request): The request object.
            exc (UserAlreadyExistsException): The UserAlreadyExistsException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "User already exists exception occurred while processing request.",
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

    @app.exception_handler(UserRepositoryException)
    async def user_repository_exception_handler(
        request: Request, exc: UserRepositoryException
    ) -> JSONResponse:
        """User repository exception handler.

        Args:
            request (Request): The request object.
            exc (UserRepositoryException): The UserRepositoryException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "User repository exception occurred while processing request.",
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

    @app.exception_handler(LibrarianAlreadyExistsException)
    async def librarian_already_exists_exception_handler(
        request: Request, exc: LibrarianAlreadyExistsException
    ) -> JSONResponse:
        """Librarian already exists exception handler.

        Args:
            request (Request): The request object.
            exc (LibrarianAlreadyExistsException): The LibrarianAlreadyExistsException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Librarian already exists exception occurred while processing request.",
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
