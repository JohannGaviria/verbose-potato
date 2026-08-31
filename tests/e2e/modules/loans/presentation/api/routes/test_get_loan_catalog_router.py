from collections.abc import Callable
from math import ceil
from typing import Any
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.e2e, pytest.mark.db]

GET_LOAN_CATALOG_URL = "/api/v1/loans/"
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


class TestGetLoanCatalog:
    class TestSuccess:
        def test_should_return_ok_when_request_is_valid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            _record_loan(client, member_auth_headers, register_loan_book())

            response = client.get(
                url=GET_LOAN_CATALOG_URL, headers=librarian_auth_headers
            )

            assert response.status_code == status.HTTP_200_OK

        def test_should_return_expected_envelope_and_default_pagination(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            loan = _record_loan(client, member_auth_headers, register_loan_book())

            response = client.get(
                url=GET_LOAN_CATALOG_URL, headers=librarian_auth_headers
            )

            body = response.json()
            assert response.status_code == status.HTTP_200_OK
            assert body["status"] == "success"
            assert body["message"] == "Loan catalog retrieved successfully."

            data = body["data"]
            assert isinstance(data["items"], list)
            assert data["page"] == 1
            assert data["page_size"] == 20
            assert data["total"] >= 1
            assert data["total_pages"] == ceil(data["total"] / data["page_size"])

            item = data["items"][0]
            assert isinstance(UUID(item["id"]), UUID)
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
            assert isinstance(UUID(item["member_id"]), UUID)
            assert isinstance(UUID(item["book_id"]), UUID)

            assert any(
                catalog_item["id"] == loan["id"] for catalog_item in data["items"]
            )

        def test_should_return_loans_from_all_members(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            member_auth_headers: dict[str, str],
            register_member_headers: RegisterMemberHeadersFactory,
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            _record_loan(client, member_auth_headers, register_loan_book())
            other_member = register_member_headers()
            _record_loan(client, other_member, register_loan_book())

            response = client.get(
                url=GET_LOAN_CATALOG_URL, headers=librarian_auth_headers
            )

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert data["total"] >= 2

        def test_should_filter_by_member_id(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            loan = _record_loan(client, member_auth_headers, register_loan_book())

            response = client.get(
                url=GET_LOAN_CATALOG_URL,
                params={"member_id": loan["member_id"]},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert data["total"] == 1
            assert data["items"][0]["member_id"] == loan["member_id"]

        def test_should_filter_by_book_id(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            loan = _record_loan(client, member_auth_headers, register_loan_book())

            response = client.get(
                url=GET_LOAN_CATALOG_URL,
                params={"book_id": loan["book_id"]},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert data["total"] == 1
            assert data["items"][0]["book_id"] == loan["book_id"]

        def test_should_filter_by_active_status(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            _record_loan(client, member_auth_headers, register_loan_book())

            response = client.get(
                url=GET_LOAN_CATALOG_URL,
                params={"status": "ACTIVE"},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert all(item["status"] == "ACTIVE" for item in data["items"])

        def test_should_return_empty_items_when_no_loans_match_filters(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(
                url=GET_LOAN_CATALOG_URL,
                params={"member_id": str(UUID(int=1))},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert data["items"] == []
            assert data["total"] == 0
            assert data["total_pages"] == 0

    class TestUnauthorized:
        def test_should_return_unauthorized_when_token_is_missing(
            self, client: TestClient
        ) -> None:
            response = client.get(url=GET_LOAN_CATALOG_URL)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["status"] == "error"

        def test_should_return_bad_request_when_token_is_invalid(
            self, client: TestClient
        ) -> None:
            response = client.get(
                url=GET_LOAN_CATALOG_URL,
                headers={"Authorization": "Bearer invalid-token"},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

    class TestForbidden:
        def test_should_return_forbidden_when_user_is_not_a_librarian(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()
            _record_loan(client, member_auth_headers, book)

            response = client.get(url=GET_LOAN_CATALOG_URL, headers=member_auth_headers)

            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert response.json()["status"] == "error"

    class TestUnprocessableEntity:
        def test_should_return_unprocessable_entity_when_member_id_is_invalid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(
                url=GET_LOAN_CATALOG_URL,
                params={"member_id": "not-a-uuid"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_book_id_is_invalid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(
                url=GET_LOAN_CATALOG_URL,
                params={"book_id": "not-a-uuid"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_status_is_invalid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(
                url=GET_LOAN_CATALOG_URL,
                params={"status": "not-a-valid-status"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_sort_by_is_invalid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(
                url=GET_LOAN_CATALOG_URL,
                params={"sort_by": "not-a-valid-field"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_sort_order_is_invalid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(
                url=GET_LOAN_CATALOG_URL,
                params={"sort_order": "not-a-valid-order"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()
