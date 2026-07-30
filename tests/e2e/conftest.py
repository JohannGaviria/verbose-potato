import asyncio
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings
from src.shared.infrastructure.persistence.models.base_model import Base
from tests.fixtures.database import (
    _db_schema,  # noqa: F401
)


@pytest.fixture
def app() -> FastAPI:
    # Imported lazily so module import order doesn't trigger side effects
    # (settings loading, logging configuration) before pytest is ready.
    from src.main import app as fastapi_app

    return fastapi_app


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    """A TestClient whose app lifespan runs for real, then a clean slate."""
    with TestClient(app) as test_client:
        yield test_client

    asyncio.run(_clear_all_tables())


async def _clear_all_tables() -> None:
    """Delete every row from every registered table, children first."""
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(table.delete())
    finally:
        await engine.dispose()
