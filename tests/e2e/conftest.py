from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def app() -> FastAPI:
    # Imported lazily so module import order doesn't trigger side effects
    # (settings loading, logging configuration) before pytest is ready.
    from src.main import app as fastapi_app

    return fastapi_app


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    # Using the TestClient as a context manager runs the app's lifespan,
    # so the database and Redis connections used by /health are real.
    with TestClient(app) as test_client:
        yield test_client
