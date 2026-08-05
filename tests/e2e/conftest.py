from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

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
