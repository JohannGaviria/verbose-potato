"""This module contains the authentication exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.domain.exceptions.authentication_exception import (
    InvalidAccessTokenClaimsException,
    InvalidAccessTokenException,
    InvalidAccessTokenPayloadException,
    InvalidAccessTokenResultException,
    InvalidCredentialsException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def authentication_exception_handlers(app: FastAPI) -> None:
    """Register the authentication exception handlers.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(InvalidAccessTokenClaimsException)
    async def invalid_access_token_claims_exception_handler(
        request: Request, exc: InvalidAccessTokenClaimsException
    ) -> JSONResponse:
        """Invalid access token claims exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidAccessTokenClaimsException): The InvalidAccessTokenClaimsException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid access token claims exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=400,
            content=JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(
                    ErrorsResponseSchema(
                        message=str(exc),
                        details=exc.error,
                    ),
                    exclude_none=True,
                ),
            ),
        )

    @app.exception_handler(InvalidAccessTokenResultException)
    async def invalid_access_token_result_exception_handler(
        request: Request, exc: InvalidAccessTokenResultException
    ) -> JSONResponse:
        """Invalid access token result exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidAccessTokenResultException): The InvalidAccessTokenResultException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid access token result exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=400,
            content=JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(
                    ErrorsResponseSchema(
                        message=str(exc),
                        details=exc.error,
                    ),
                    exclude_none=True,
                ),
            ),
        )

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

    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials_exception_handler(
        request: Request, exc: InvalidCredentialsException
    ) -> JSONResponse:
        """Invalid credentials exception handler.

        Args:
            request (Request): The request object.
            exc (InvalidCredentialsException): The InvalidCredentialsException exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Invalid credentials exception occurred while processing request.",
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
