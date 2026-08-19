from collections.abc import Callable
from typing import Any
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.e2e, pytest.mark.db]

REGISTER_BOOK_URL = "/api/v1/books/register"

RegisterBookPayloadFactory = Callable[[], dict[str, Any]]


def _delete_book_url(book_id: str) -> str:
    return f"/api/v1/books/{book_id}"


def _register_book(
    client: TestClient,
    auth_headers: dict[str, str],
    register_book_payload: RegisterBookPayloadFactory,
    **overrides: Any,
) -> dict[str, Any]:
    payload = register_book_payload() | overrides
    response = client.post(url=REGISTER_BOOK_URL, json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return dict(response.json()["data"])


class TestDeleteBook:
    class TestSuccess:
        def test_should_return_no_content_when_deletion_is_successful(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            book = _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.delete(
                url=_delete_book_url(book["id"]),
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert response.content == b""

        def test_should_remove_book_when_deletion_is_successful(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            book = _register_book(client, librarian_auth_headers, register_book_payload)

            client.delete(
                url=_delete_book_url(book["id"]),
                headers=librarian_auth_headers,
            )

            response = client.delete(
                url=_delete_book_url(book["id"]),
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["status"] == "error"

    class TestUnauthorized:
        def test_should_return_unauthorized_when_no_token_is_provided(
            self, client: TestClient
        ) -> None:
            response = client.delete(url=_delete_book_url(str(uuid4())))

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["status"] == "error"

        def test_should_return_bad_request_when_token_is_invalid(
            self, client: TestClient
        ) -> None:
            response = client.delete(
                url=_delete_book_url(str(uuid4())),
                headers={"Authorization": "Bearer not-a-real-token"},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

    class TestForbidden:
        def test_should_return_forbidden_when_authenticated_user_is_not_librarian(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
        ) -> None:
            response = client.delete(
                url=_delete_book_url(str(uuid4())),
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert response.json()["status"] == "error"

    class TestNotFound:
        def test_should_return_not_found_when_book_does_not_exist(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
        ) -> None:
            response = client.delete(
                url=_delete_book_url(str(uuid4())),
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["status"] == "error"

    class TestUnprocessableEntity:
        def test_should_return_unprocessable_entity_when_book_id_is_not_a_valid_uuid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
        ) -> None:
            response = client.delete(
                url=_delete_book_url("not-a-uuid"),
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
