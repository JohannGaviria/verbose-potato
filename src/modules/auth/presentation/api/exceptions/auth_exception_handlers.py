"""This module contains the auth exception handlers."""

from fastapi import FastAPI

from src.modules.auth.presentation.api.exceptions.credentials_exception_handlers import (
    credentials_exception_handlers,
)
from src.modules.auth.presentation.api.exceptions.user_exception_handlers import (
    user_exception_handlers,
)


def auth_exception_handlers(app: FastAPI) -> None:
    """Register the auth exception handlers.

    Args:
        app (FastAPI): The FastAPI application.
    """
    credentials_exception_handlers(app)
    user_exception_handlers(app)
