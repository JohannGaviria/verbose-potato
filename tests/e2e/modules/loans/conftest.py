from collections.abc import Callable
from datetime import date
from typing import Any

import pytest
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient

from tests.conftest import _generate_isbn13

REGISTER_BOOK_URL = "/api/v1/books/register"
REGISTER_MEMBER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"


@pytest.fixture
def loan_book_payload(faker: Faker) -> Callable[..., dict[str, Any]]:
    """Factory for a valid loanable book registration payload."""

    def _make(**overrides: Any) -> dict[str, Any]:
        payload = {
            "title": faker.sentence(nb_words=4),
            "isbn": _generate_isbn13(faker),
            "author": faker.name(),
            "published_year": faker.random_int(min=1450, max=date.today().year),
            "total_copies": faker.random_int(min=1, max=5),
        }
        payload.update(overrides)
        return payload

    return _make


@pytest.fixture
def register_loan_book(
    client: TestClient,
    librarian_auth_headers: dict[str, str],
    loan_book_payload: Callable[..., dict[str, Any]],
) -> Callable[..., dict[str, Any]]:
    """Registers a book through the API and returns the registered book data."""

    def _register(**overrides: Any) -> dict[str, Any]:
        payload = loan_book_payload(**overrides)
        response = client.post(
            url=REGISTER_BOOK_URL, json=payload, headers=librarian_auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        return dict(response.json()["data"])

    return _register


@pytest.fixture
def register_member_headers(
    client: TestClient,
    faker: Faker,
) -> Callable[[], dict[str, str]]:
    """Registers and logs in a fresh member, returning its bearer auth headers."""

    def _register() -> dict[str, str]:
        password = faker.password(
            length=16,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        )
        payload = {
            "name": faker.name(),
            "email": faker.unique.email(),
            "password": password,
        }
        response = client.post(url=REGISTER_MEMBER_URL, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        login_response = client.post(
            url=LOGIN_URL, json={"email": payload["email"], "password": password}
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["data"]["access_token"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _register
