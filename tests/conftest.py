import asyncio
from collections.abc import Iterator

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import (
    create_async_engine,
)

from src.config import settings
from src.shared.infrastructure.persistence.models.base_model import Base


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture(scope="session", autouse=True)
def _db_schema() -> Iterator[None]:
    """Create every registered table once for the whole integration test session."""

    async def _create() -> None:
        engine = create_async_engine(settings.DATABASE_URL)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        finally:
            await engine.dispose()

    async def _drop() -> None:
        engine = create_async_engine(settings.DATABASE_URL)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        finally:
            await engine.dispose()

    asyncio.run(_create())
    yield
    asyncio.run(_drop())
