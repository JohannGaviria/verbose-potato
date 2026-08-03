"""This module contains the exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def exception_handlers(app: FastAPI) -> None:
    """Register the exception handlers.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Exception handler.

        Args:
            request (Request): The request object.
            exc (Exception): The Exception exception.

        Returns:
            JSONResponse: The JSON response with the appropriate status code and message.
        """
        _logger.error(
            "Exception occurred while processing request.",
            request_method=request.method,
            request_path=request.url.path,
            exception_message=exc,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )
