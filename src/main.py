"""This module contains the main application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.shared.infrastructure.cache.redis_client import redis_client
from src.shared.infrastructure.database.database import db
from src.shared.infrastructure.logging.structlog_configure_logging import (
    StructlogConfigureLogging,
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
