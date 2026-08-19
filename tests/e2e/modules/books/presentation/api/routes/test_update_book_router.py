from collections.abc import Callable
from typing import Any
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.e2e, pytest.mark.db]

REGISTER_BOOK_URL = "/api/v1/books/register"

RegisterBookPayloadFactory = Callable[[], dict[str, Any]]


def _update_book_url(book_id: str) -> str:
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


class TestUpdateBook:
    class TestSuccess:
        def test_should_return_ok_when_update_data_is_valid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            book = _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.patch(
                url=_update_book_url(book["id"]),
                json={"title": "Updated Title"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK

        def test_should_return_updated_book_data_when_all_fields_are_provided(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            book = _register_book(client, librarian_auth_headers, register_book_payload)

            new_data = {
                "title": "Updated Title",
                "author": "Updated Author",
                "published_year": 2015,
                "total_copies": book["total_copies"] + 5,
            }

            response = client.patch(
                url=_update_book_url(book["id"]),
                json=new_data,
                headers=librarian_auth_headers,
            )

            body = response.json()
            assert body["status"] == "success"
            assert body["message"] == "Book updated successfully."

            data = body["data"]
            assert data["id"] == book["id"]
            assert data["isbn"] == book["isbn"]
            assert data["title"] == new_data["title"]
            assert data["author"] == new_data["author"]
            assert data["published_year"] == new_data["published_year"]
            assert data["total_copies"] == new_data["total_copies"]
            assert data["available_copies"] == book["available_copies"]
            assert data["created_at"] == book["created_at"]
            assert data["updated_at"] != book["updated_at"]

        def test_should_keep_unprovided_fields_unchanged_when_partial_update(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            book = _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.patch(
                url=_update_book_url(book["id"]),
                json={"title": "Only Title Changed"},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            assert data["title"] == "Only Title Changed"
            assert data["author"] == book["author"]
            assert data["published_year"] == book["published_year"]
            assert data["total_copies"] == book["total_copies"]
            assert data["isbn"] == book["isbn"]

        def test_should_return_ok_and_keep_book_unchanged_when_body_is_empty(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            book = _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.patch(
                url=_update_book_url(book["id"]),
                json={},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK

            data = response.json()["data"]
            assert data["title"] == book["title"]
            assert data["author"] == book["author"]
            assert data["published_year"] == book["published_year"]
            assert data["total_copies"] == book["total_copies"]

    class TestUnauthorized:
        def test_should_return_unauthorized_when_no_token_is_provided(
            self, client: TestClient
        ) -> None:
            response = client.patch(
                url=_update_book_url(str(uuid4())), json={"title": "New Title"}
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["status"] == "error"

        def test_should_return_bad_request_when_token_is_invalid(
            self, client: TestClient
        ) -> None:
            response = client.patch(
                url=_update_book_url(str(uuid4())),
                json={"title": "New Title"},
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
            response = client.patch(
                url=_update_book_url(str(uuid4())),
                json={"title": "New Title"},
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
            response = client.patch(
                url=_update_book_url(str(uuid4())),
                json={"title": "New Title"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["status"] == "error"

    class TestInvalidFormat:
        @pytest.mark.parametrize("title", ["ab", "a" * 256])
        def test_should_return_bad_request_when_title_format_is_invalid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
            title: str,
        ) -> None:
            book = _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.patch(
                url=_update_book_url(book["id"]),
                json={"title": title},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize("author", ["ab", "a" * 101])
        def test_should_return_bad_request_when_author_format_is_invalid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
            author: str,
        ) -> None:
            book = _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.patch(
                url=_update_book_url(book["id"]),
                json={"author": author},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize("published_year", [1449, 3000])
        def test_should_return_bad_request_when_published_year_is_out_of_range(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
            published_year: int,
        ) -> None:
            book = _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.patch(
                url=_update_book_url(book["id"]),
                json={"published_year": published_year},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize("total_copies", [0, -1])
        def test_should_return_bad_request_when_total_copies_is_invalid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
            total_copies: int,
        ) -> None:
            book = _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.patch(
                url=_update_book_url(book["id"]),
                json={"total_copies": total_copies},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        def test_should_return_bad_request_when_total_copies_is_less_than_available_copies(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            book = _register_book(
                client,
                librarian_auth_headers,
                register_book_payload,
                total_copies=5,
            )

            response = client.patch(
                url=_update_book_url(book["id"]),
                json={"total_copies": book["total_copies"] - 1},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

    class TestUnprocessableEntity:
        @pytest.mark.parametrize("malformed_field", ["published_year", "total_copies"])
        def test_should_return_unprocessable_entity_when_field_has_wrong_type(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
            malformed_field: str,
        ) -> None:
            book = _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.patch(
                url=_update_book_url(book["id"]),
                json={malformed_field: "not-a-number"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_book_id_is_not_a_valid_uuid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
        ) -> None:
            response = client.patch(
                url=_update_book_url("not-a-uuid"),
                json={"title": "New Title"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        def test_should_return_unprocessable_entity_when_no_body_is_sent(
            self, client: TestClient, librarian_auth_headers: dict[str, str]
        ) -> None:
            response = client.patch(
                url=_update_book_url(str(uuid4())), headers=librarian_auth_headers
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
