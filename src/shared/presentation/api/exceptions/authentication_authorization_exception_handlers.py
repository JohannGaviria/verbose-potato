"""This module contains the authentication and authorization exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.shared.domain.exceptions.authentication_authorization_exception import (
    AuthenticationTokenMissingException,
    ExpiredAccessTokenException,
    InsufficientPermissionsException,
    InvalidAccessTokenException,
    InvalidAccessTokenPayloadException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def authentication_authorization_exception_handlers(app: FastAPI) -> None:
    """Register the authentication and authorization exception handlers.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(InvalidAccessTokenException)
    async def invalid_access_token_exception_handler(
        request: Request, exc: InvalidAccessTokenException
    ) -> JSONResponse:
        """Invalid access token exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidAccessTokenException): The InvalidAccessTokenException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid access token exception occurred while processing request.",
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

    @app.exception_handler(InvalidAccessTokenPayloadException)
    async def invalid_access_token_payload_exception_handler(
        request: Request, exc: InvalidAccessTokenPayloadException
    ) -> JSONResponse:
        """Invalid access token payload exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidAccessTokenPayloadException): The InvalidAccessTokenPayloadException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid access token payload exception occurred while processing request.",
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

    @app.exception_handler(ExpiredAccessTokenException)
    async def expired_access_token_exception_handler(
        request: Request, exc: ExpiredAccessTokenException
    ) -> JSONResponse:
        """Expired access token exception handler.

        Args:
            request (Request): The request object.
            exc (ExpiredAccessTokenException): The ExpiredAccessTokenException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Expired access token exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(AuthenticationTokenMissingException)
    async def authentication_token_missing_exception_handler(
        request: Request, exc: AuthenticationTokenMissingException
    ) -> JSONResponse:
        """Authentication token missing exception handler.

        Args:
            request (Request): The request object.
            exc (AuthenticationTokenMissingException): The AuthenticationTokenMissingException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Authentication token missing exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(InsufficientPermissionsException)
    async def insufficient_permissions_exception_handler(
        request: Request, exc: InsufficientPermissionsException
    ) -> JSONResponse:
        """Insufficient permissions exception handler.

        Args:
            request (Request): The request object.
            exc (InsufficientPermissionsException): The InsufficientPermissionsException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Insufficient permissions exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    details=exc.error,
                ),
                exclude_none=True,
            ),
        )
