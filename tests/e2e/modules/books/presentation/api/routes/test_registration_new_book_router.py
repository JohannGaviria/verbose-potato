from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.e2e, pytest.mark.db]

REGISTER_BOOK_URL = "/api/v1/books/register"

RegisterBookPayloadFactory = Callable[[], dict[str, Any]]


class TestRegistrationNewBook:
    class TestSuccess:
        def test_should_return_created_when_registration_data_is_valid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            payload = register_book_payload()

            response = client.post(
                url=REGISTER_BOOK_URL, json=payload, headers=librarian_auth_headers
            )

            assert response.status_code == status.HTTP_201_CREATED

        def test_should_return_created_book_data_when_registration_succeeds(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            payload = register_book_payload()

            response = client.post(
                url=REGISTER_BOOK_URL, json=payload, headers=librarian_auth_headers
            )

            body = response.json()
            assert body["status"] == "success"
            assert body["message"] == "Book registered successfully."

            data = body["data"]
            assert UUID(data["id"])
            assert data["title"] == payload["title"]
            assert data["isbn"] == payload["isbn"]
            assert data["author"] == payload["author"]
            assert data["published_year"] == payload["published_year"]
            assert data["total_copies"] == payload["total_copies"]
            assert data["available_copies"] == payload["total_copies"]
            assert data["created_at"]
            assert data["updated_at"]

        def test_should_allow_registering_several_different_books(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            first_response = client.post(
                url=REGISTER_BOOK_URL,
                json=register_book_payload(),
                headers=librarian_auth_headers,
            )
            second_response = client.post(
                url=REGISTER_BOOK_URL,
                json=register_book_payload(),
                headers=librarian_auth_headers,
            )

            assert first_response.status_code == status.HTTP_201_CREATED
            assert second_response.status_code == status.HTTP_201_CREATED
            assert (
                first_response.json()["data"]["id"]
                != second_response.json()["data"]["id"]
            )

    class TestUnauthorized:
        def test_should_return_unauthorized_when_no_token_is_provided(
            self,
            client: TestClient,
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            response = client.post(url=REGISTER_BOOK_URL, json=register_book_payload())

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["status"] == "error"

        def test_should_return_unauthorized_when_token_is_invalid(
            self,
            client: TestClient,
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            response = client.post(
                url=REGISTER_BOOK_URL,
                json=register_book_payload(),
                headers={"Authorization": "Bearer not-a-real-token"},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

    class TestForbidden:
        def test_should_return_forbidden_when_authenticated_user_is_not_librarian(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            response = client.post(
                url=REGISTER_BOOK_URL,
                json=register_book_payload(),
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert response.json()["status"] == "error"

    class TestInvalidFormat:
        @pytest.mark.parametrize("title", ["", "ab", "a" * 256])
        def test_should_return_bad_request_when_title_format_is_invalid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
            title: str,
        ) -> None:
            payload = register_book_payload()
            payload["title"] = title

            response = client.post(
                url=REGISTER_BOOK_URL, json=payload, headers=librarian_auth_headers
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize("author", ["", "ab", "a" * 101])
        def test_should_return_bad_request_when_author_format_is_invalid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
            author: str,
        ) -> None:
            payload = register_book_payload()
            payload["author"] = author

            response = client.post(
                url=REGISTER_BOOK_URL, json=payload, headers=librarian_auth_headers
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize("isbn", ["", "123", "9780306406158", "not-an-isbn"])
        def test_should_return_bad_request_when_isbn_format_is_invalid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
            isbn: str,
        ) -> None:
            payload = register_book_payload()
            payload["isbn"] = isbn

            response = client.post(
                url=REGISTER_BOOK_URL, json=payload, headers=librarian_auth_headers
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
            payload = register_book_payload()
            payload["published_year"] = published_year

            response = client.post(
                url=REGISTER_BOOK_URL, json=payload, headers=librarian_auth_headers
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
            payload = register_book_payload()
            payload["total_copies"] = total_copies

            response = client.post(
                url=REGISTER_BOOK_URL, json=payload, headers=librarian_auth_headers
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

    class TestConflict:
        def test_should_return_conflict_when_isbn_is_already_registered(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            payload = register_book_payload()

            first_response = client.post(
                url=REGISTER_BOOK_URL, json=payload, headers=librarian_auth_headers
            )
            assert first_response.status_code == status.HTTP_201_CREATED

            second_payload = register_book_payload()
            second_payload["isbn"] = payload["isbn"]

            response = client.post(
                url=REGISTER_BOOK_URL,
                json=second_payload,
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_409_CONFLICT
            assert response.json()["status"] == "error"

    class TestUnprocessableEntity:
        @pytest.mark.parametrize(
            "missing_field",
            ["title", "isbn", "author", "published_year", "total_copies"],
        )
        def test_should_return_unprocessable_entity_when_required_field_is_missing(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
            missing_field: str,
        ) -> None:
            payload = register_book_payload()
            del payload[missing_field]

            response = client.post(
                url=REGISTER_BOOK_URL, json=payload, headers=librarian_auth_headers
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        @pytest.mark.parametrize("malformed_field", ["published_year", "total_copies"])
        def test_should_return_unprocessable_entity_when_field_has_wrong_type(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
            malformed_field: str,
        ) -> None:
            payload = register_book_payload()
            payload[malformed_field] = "not-a-number"

            response = client.post(
                url=REGISTER_BOOK_URL, json=payload, headers=librarian_auth_headers
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_body_is_empty(
            self, client: TestClient, librarian_auth_headers: dict[str, str]
        ) -> None:
            response = client.post(
                url=REGISTER_BOOK_URL, json={}, headers=librarian_auth_headers
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        def test_should_return_unprocessable_entity_when_no_body_is_sent(
            self, client: TestClient, librarian_auth_headers: dict[str, str]
        ) -> None:
            response = client.post(
                url=REGISTER_BOOK_URL, headers=librarian_auth_headers
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
