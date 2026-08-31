from collections.abc import Callable
from math import ceil
from typing import Any
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.e2e, pytest.mark.db]

GET_MY_LOANS_URL = "/api/v1/loans/me"
RECORDING_LOAN_URL = "/api/v1/loans/"

RegisterLoanBookFactory = Callable[..., dict[str, Any]]
RegisterMemberHeadersFactory = Callable[[], dict[str, str]]


def _record_loan(
    client: TestClient,
    auth_headers: dict[str, str],
    book: dict[str, Any],
) -> dict[str, Any]:
    response = client.post(
        url=RECORDING_LOAN_URL,
        json={"book_id": book["id"]},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    return dict(response.json()["data"])


class TestGetMyLoans:
    class TestSuccess:
        def test_should_return_ok_when_request_is_valid(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()
            _record_loan(client, member_auth_headers, book)

            response = client.get(url=GET_MY_LOANS_URL, headers=member_auth_headers)

            assert response.status_code == status.HTTP_200_OK

        def test_should_return_expected_envelope_and_default_pagination(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()
            loan = _record_loan(client, member_auth_headers, book)

            response = client.get(url=GET_MY_LOANS_URL, headers=member_auth_headers)

            body = response.json()
            assert response.status_code == status.HTTP_200_OK
            assert body["status"] == "success"
            assert body["message"] == "Member loans retrieved successfully."

            data = body["data"]
            assert isinstance(data["items"], list)
            assert data["page"] == 1
            assert data["page_size"] == 20
            assert data["total"] >= 1
            assert data["total_pages"] == ceil(data["total"] / data["page_size"])

            item = data["items"][0]
            assert item["id"] == loan["id"]
            assert {
                "id",
                "member_id",
                "book_id",
                "status",
                "loaned_at",
                "returned_at",
                "created_at",
                "updated_at",
            }.issubset(item.keys())
            assert isinstance(UUID(item["id"]), UUID)

        def test_should_return_only_the_authenticated_member_loans(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_member_headers: RegisterMemberHeadersFactory,
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()
            _record_loan(client, member_auth_headers, book)

            other_member = register_member_headers()
            _record_loan(client, other_member, register_loan_book())

            response = client.get(url=GET_MY_LOANS_URL, headers=member_auth_headers)

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert data["total"] == 1
            assert data["items"][0]["book_id"] == book["id"]

        def test_should_filter_loans_by_status(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_member_headers: RegisterMemberHeadersFactory,
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()
            _record_loan(client, member_auth_headers, book)

            other_member = register_member_headers()
            _record_loan(client, other_member, register_loan_book())

            response = client.get(
                url=GET_MY_LOANS_URL,
                params={"status": "ACTIVE"},
                headers=member_auth_headers,
            )

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert data["total"] == 1
            assert data["items"][0]["status"] == "ACTIVE"

    class TestUnauthorized:
        def test_should_return_unauthorized_when_token_is_missing(
            self, client: TestClient
        ) -> None:
            response = client.get(url=GET_MY_LOANS_URL)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["status"] == "error"

        def test_should_return_bad_request_when_token_is_invalid(
            self, client: TestClient
        ) -> None:
            response = client.get(
                url=GET_MY_LOANS_URL,
                headers={"Authorization": "Bearer invalid-token"},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

    class TestForbidden:
        def test_should_return_forbidden_when_user_is_not_a_member(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(url=GET_MY_LOANS_URL, headers=librarian_auth_headers)

            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert response.json()["status"] == "error"

    class TestEmptyResult:
        def test_should_return_empty_items_when_member_has_no_loans(
            self,
            client: TestClient,
            register_member_headers: RegisterMemberHeadersFactory,
        ) -> None:
            response = client.get(
                url=GET_MY_LOANS_URL, headers=register_member_headers()
            )

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert data["items"] == []
            assert data["total"] == 0
            assert data["total_pages"] == 0

    class TestUnprocessableEntity:
        def test_should_return_unprocessable_entity_when_status_is_invalid(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(
                url=GET_MY_LOANS_URL,
                params={"status": "not-a-valid-status"},
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_sort_by_is_invalid(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(
                url=GET_MY_LOANS_URL,
                params={"sort_by": "not-a-valid-field"},
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_sort_order_is_invalid(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(
                url=GET_MY_LOANS_URL,
                params={"sort_order": "not-a-valid-order"},
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_page_is_not_an_integer(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(
                url=GET_MY_LOANS_URL,
                params={"page": "not-a-number"},
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()
