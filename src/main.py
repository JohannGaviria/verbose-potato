"""This module contains the main application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.modules.auth.presentation.api.exceptions.auth_exception_handlers import (
    auth_exception_handlers,
)
from src.modules.auth.presentation.api.routes.auth_router import router as auth_router
from src.modules.auth.presentation.compositions.runner_composition import (
    get_create_first_librarian_runner,
)
from src.modules.books.presentation.api.exceptions.book_exception_handlers import (
    book_exception_handlers,
)
from src.modules.books.presentation.api.routes.books_router import (
    router as books_router,
)
from src.modules.loans.presentation.api.exceptions.loan_exception_handlers import (
    loan_exception_handlers,
)
from src.modules.loans.presentation.api.routes.loans_router import (
    router as loans_router,
)
from src.shared.infrastructure.cache.redis_client import redis_client
from src.shared.infrastructure.database.database import db
from src.shared.infrastructure.logging.structlog_configure_logging import (
    StructlogConfigureLogging,
)
from src.shared.presentation.api.exceptions.exception_handlers import exception_handlers
from src.shared.presentation.api.middleware.correlation_id_middleware import (
    CorrelationIdMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager for managing database and Redis connections.

    This context manager ensures that the database and Redis connections are properly
    established and closed when the application starts and stops.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    # Startup: open database and Redis connections once per process.
    db.connect()
    redis_client.connect()

    # Seed the database with the first librarian account.
    runner = get_create_first_librarian_runner()
    await runner.run()

    yield
    # Shutdown: close database and Redis connections once per process.
    await redis_client.disconnect()
    await db.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    summary=settings.APP_SUMMARY,
    description=settings.APP_DESCRIPTION,
    debug=settings.DEBUG,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# Configure logging using Structlog
StructlogConfigureLogging.configure(debug=settings.DEBUG)


allow_origins = [
    origin.strip()
    for origin in settings.CORS_ALLOW_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Includes the middleware for the API endpoints
app.add_middleware(CorrelationIdMiddleware)


# Includes the exception handlers for the API endpoints
exception_handlers(app)
auth_exception_handlers(app)
book_exception_handlers(app)
loan_exception_handlers(app)


# Includes the routers for the API endpoints
app.include_router(auth_router)
app.include_router(books_router)
app.include_router(loans_router)


@app.get(
    path="/",
    tags=["System"],
    summary="Root Endpoint",
    description="Returns a welcome message.",
)
async def root() -> JSONResponse:
    """Root endpoint that returns a welcome message.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return JSONResponse(
        content={
            "message": f"Welcome to the {settings.APP_NAME}, version {settings.APP_VERSION}!"
        },
        status_code=status.HTTP_200_OK,
    )


@app.get(
    path="/health",
    tags=["System"],
    summary="Health Check Endpoint",
    description="Checks the operational status of the server, PostgreSQL, and Redis.",
)
async def health_check() -> JSONResponse:
    """Health check endpoint that verifies the status of the server, PostgreSQL, and Redis.

    Returns:
        dict: A dictionary containing the health status of the services.
    """
    db_status = await db.ping()
    redis_status = await redis_client.ping()

    payload = {
        "status": "healthy" if db_status and redis_status else "unhealthy",
        "database": db_status,
        "redis": redis_status,
    }

    status_code = (
        status.HTTP_200_OK
        if db_status and redis_status
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(content=payload, status_code=status_code)
