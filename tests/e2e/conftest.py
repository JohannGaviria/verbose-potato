from collections.abc import Callable, Iterator
from typing import Any

import pytest
from faker import Faker
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from src.config import settings
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


def _valid_password(faker: Faker) -> str:
    """Builds a password that satisfies every complexity rule."""
    return faker.password(
        length=16,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )


RegisterUserPayloadFactory = Callable[[], dict[str, Any]]


@pytest.fixture
def register_member_payload(faker: Faker) -> RegisterUserPayloadFactory:
    """Factory for a valid member registration payload."""

    def _make() -> dict[str, Any]:
        return {
            "name": faker.name(),
            "email": faker.unique.email(),
            "password": _valid_password(faker),
        }

    return _make


def _login(client: TestClient, email: str, password: str) -> str:
    """Logs in through the API and returns the issued access token."""
    response = client.post(
        url="/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == status.HTTP_200_OK
    return str(response.json()["data"]["access_token"]["access_token"])


@pytest.fixture
def librarian_auth_headers(client: TestClient) -> dict[str, str]:
    """Bearer auth headers for the librarian seeded on application startup."""
    token = _login(
        client,
        email=settings.FIRST_LIBRARIES_EMAIL,
        password=settings.FIRST_LIBRARIES_PASSWORD,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def member_auth_headers(
    client: TestClient,
    register_member_payload: RegisterUserPayloadFactory,
) -> dict[str, str]:
    """Bearer auth headers for a freshly registered member."""
    payload = register_member_payload()
    response = client.post(url="/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    token = _login(client, email=payload["email"], password=payload["password"])
    return {"Authorization": f"Bearer {token}"}
