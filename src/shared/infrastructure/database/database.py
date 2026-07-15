"""This module contains the Database class."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings


class Database:
    """Manages database connections and sessions."""

    def __init__(self) -> None:
        """Initializes the database."""
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None
        self._logger = structlog.get_logger(__name__)

    def connect(self) -> None:
        """Creates the engine and sessionmaker identifier. Idempotent."""
        if self._engine is not None:
            self._logger.debug("Database already connected.")
            return

        self._logger.debug("Connecting to database...")
        self._engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DB_ECHO,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_pre_ping=True,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        self._logger.debug("Database connected.")

    async def disconnect(self) -> None:
        """Closes the database connection pool. Idempotent."""
        if self._engine is not None:
            self._logger.debug("Disconnecting from database...")
            await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None
        self._logger.debug("Database disconnected.")

    async def ping(self) -> bool:
        """Health check for the database connection."""
        if self._engine is None:
            self._logger.debug("Database not connected. Calling connect()...")
            raise RuntimeError("Database not connected. Call connect() first.")

        async with self._engine.connect() as conn:
            self._logger.debug("Pinging database...")
            await conn.execute(text("SELECT 1"))
        self._logger.debug("Database ping successful.")
        return True

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Context manager that provides a session and ensures its closure.

        It does not automatically commit: the caller (use case / unit of work)
        decides when to commit the transaction. In the event of an exception,
        a rollback is performed before propagating it.
        """
        if self._sessionmaker is None:
            self._logger.debug("Database not connected. Calling connect()...")
            raise RuntimeError("Database not connected. Call connect() first.")

        async with self._sessionmaker() as session:
            try:
                self._logger.debug("Session acquired.")
                yield session
            except Exception:
                self._logger.debug("Rolling back session...")
                await session.rollback()
                raise


db = Database()


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Get a db session context manager.

    Returns:
        AsyncIterator[AsyncSession]: The db session context manager.
    """
    async with db.session() as session:
        yield session
