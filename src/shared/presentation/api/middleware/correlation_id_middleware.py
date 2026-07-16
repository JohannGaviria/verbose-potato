"""This module contains the correlation id middleware class."""

from collections.abc import Callable
from uuid import uuid4

import structlog
from fastapi.requests import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware that generates a correlation_id per request and binds it to structlog context."""

    HEADER_NAME = "X-Correlation-ID"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Dispatch the request to the next middleware or the application.

        Args:
            request (Request): The FastAPI request object.
            call_next (callable): The next middleware or the application.

        Returns:
            Response: The response from the next middleware or the application.
        """
        # Generate a new correlation_id if not provided in the request headers
        correlation_id = request.headers.get(self.HEADER_NAME) or str(uuid4())

        # Bind the correlation_id to structlog context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        response = await call_next(request)

        # Add the correlation_id to the response headers
        response.headers[self.HEADER_NAME] = correlation_id
        return response
