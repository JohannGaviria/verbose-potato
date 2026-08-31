from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings
from src.modules.auth.infrastructure.persistence.models.user_model import (
    UserModel,  # noqa: F401
)
from src.modules.books.infrastructure.persistence.models.book_model import (
    BookModel,  # noqa: F401
)
from src.modules.loans.infrastructure.persistence.models.loan_model import (
    LoanModel,  # noqa: F401
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.infrastructure.cache.redis_client import redis_client as _redis_client
from src.shared.infrastructure.database.database import db as _db
from src.shared.infrastructure.outbound.pyjwt_toke_decode_outbound_adapter import (
    PyJWTTokenDecodeOutboundAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.infrastructure.persistence.models.base_model import Base
from tests.fixtures.database import (
    _db_schema,  # noqa: F401
)


async def _truncate_all(conn: AsyncConnection) -> None:
    """Remove every row from all registered tables.

    Runs before each test's outer transaction so each integration test starts
    from an empty, isolated database regardless of any committed data left by
    other suites (e.g. E2E) executed earlier in the same pytest session.
    """
    tables = ", ".join(Base.metadata.tables.keys())
    await conn.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))
    await conn.commit()


@pytest_asyncio.fixture
async def db() -> AsyncIterator[object]:
    """Provide a connected ``Database`` instance backed by a real PostgreSQL."""
    _db.connect()
    try:
        yield _db
    finally:
        await _db.disconnect()


@pytest_asyncio.fixture
async def redis_conn() -> AsyncIterator[Redis]:
    """Provide a connected Redis client backed by a real Redis instance."""
    _redis_client.connect()
    try:
        yield _redis_client.client
    finally:
        await _redis_client.disconnect()


@pytest_asyncio.fixture
async def db_connection() -> AsyncIterator[AsyncConnection]:
    """A single DB connection wrapped in an outer transaction, for one test."""
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        await _truncate_all(conn)
        await conn.begin()
        try:
            yield conn
        finally:
            await conn.rollback()
    await engine.dispose()


@pytest.fixture
def session_factory(
    db_connection: AsyncConnection,
) -> async_sessionmaker[AsyncSession]:
    """A sessionmaker whose sessions all join the same per-test transaction."""
    return async_sessionmaker(
        bind=db_connection,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )


@pytest_asyncio.fixture
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    """A single ``AsyncSession`` bound to the per-test transaction.

    Convenience fixture for tests that talk to a repository adapter
    directly, without going through a Unit of Work.
    """
    async with session_factory() as session:
        yield session


@pytest.fixture
def logger_factory_outbound() -> LoggerFactoryOutboundPort:
    """A real structlog-backed logger factory, shared by adapter fixtures."""
    return StructlogLoggerFactoryOutboundAdapter()


@pytest.fixture
def token_decode_outbound() -> PyJWTTokenDecodeOutboundAdapter:
    return PyJWTTokenDecodeOutboundAdapter(
        jwt_secret_key=settings.JWT_SECRET_KEY,
        jwt_algorithm=settings.JWT_ALGORITHM,
    )
