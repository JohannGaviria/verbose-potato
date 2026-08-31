from collections.abc import Callable
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.e2e, pytest.mark.db]

RECORDING_LOAN_URL = "/api/v1/loans/"
GET_BOOK_CATALOG_URL = "/api/v1/books/"

RegisterLoanBookFactory = Callable[..., dict[str, Any]]
RegisterMemberHeadersFactory = Callable[[], dict[str, str]]


class TestReturningLoan:
    class TestSuccess:
        def test_should_return_ok_when_loan_is_active(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()

            recording_response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=member_auth_headers,
            )
            assert recording_response.status_code == status.HTTP_201_CREATED
            loan_id = recording_response.json()["data"]["id"]

            response = client.patch(
                url=f"{RECORDING_LOAN_URL}{loan_id}/return",
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK

        def test_should_return_updated_loan_data_when_return_succeeds(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()

            recording_response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=member_auth_headers,
            )
            assert recording_response.status_code == status.HTTP_201_CREATED
            loan_data = recording_response.json()["data"]
            loan_id = loan_data["id"]

            response = client.patch(
                url=f"{RECORDING_LOAN_URL}{loan_id}/return",
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK

            body = response.json()
            assert body["status"] == "success"
            assert body["message"] == "Loan returned successfully."

            data = body["data"]
            assert isinstance(UUID(data["id"]), UUID)
            assert data["id"] == loan_data["id"]
            assert data["member_id"] == loan_data["member_id"]
            assert data["book_id"] == book["id"]
            assert data["status"] == "RETURNED"
            assert data["loaned_at"] is not None
            assert data["returned_at"] is not None

        def test_should_increase_available_copies_when_return_succeeds(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book(total_copies=1)

            recording_response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=member_auth_headers,
            )
            assert recording_response.status_code == status.HTTP_201_CREATED
            loan_id = recording_response.json()["data"]["id"]

            catalog_before = client.get(
                url=GET_BOOK_CATALOG_URL,
                headers=member_auth_headers,
                params={"isbn": book["isbn"]},
            )
            assert catalog_before.status_code == status.HTTP_200_OK
            assert catalog_before.json()["data"]["items"][0]["available_copies"] == 0

            response = client.patch(
                url=f"{RECORDING_LOAN_URL}{loan_id}/return",
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK

            catalog_after = client.get(
                url=GET_BOOK_CATALOG_URL,
                headers=member_auth_headers,
                params={"isbn": book["isbn"]},
            )
            assert catalog_after.status_code == status.HTTP_200_OK
            assert catalog_after.json()["data"]["items"][0]["available_copies"] == 1

    class TestUnauthorized:
        def test_should_return_unauthorized_when_token_is_missing(
            self,
            client: TestClient,
        ) -> None:
            response = client.patch(
                url=f"{RECORDING_LOAN_URL}{uuid4()}/return",
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        def test_should_return_bad_request_when_token_is_invalid(
            self,
            client: TestClient,
        ) -> None:
            response = client.patch(
                url=f"{RECORDING_LOAN_URL}{uuid4()}/return",
                headers={"Authorization": "Bearer invalid-token"},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    class TestForbidden:
        def test_should_return_forbidden_when_user_is_not_a_member(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
        ) -> None:
            response = client.patch(
                url=f"{RECORDING_LOAN_URL}{uuid4()}/return",
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_403_FORBIDDEN

        def test_should_return_forbidden_when_loan_belongs_to_another_member(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_member_headers: RegisterMemberHeadersFactory,
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()

            recording_response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=member_auth_headers,
            )
            assert recording_response.status_code == status.HTTP_201_CREATED
            loan_id = recording_response.json()["data"]["id"]

            response = client.patch(
                url=f"{RECORDING_LOAN_URL}{loan_id}/return",
                headers=register_member_headers(),
            )

            assert response.status_code == status.HTTP_403_FORBIDDEN

    class TestNotFound:
        def test_should_return_not_found_when_loan_does_not_exist(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
        ) -> None:
            response = client.patch(
                url=f"{RECORDING_LOAN_URL}{uuid4()}/return",
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["message"] == "Loan cannot be found."

    class TestConflict:
        def test_should_return_conflict_when_loan_is_already_returned(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()

            recording_response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=member_auth_headers,
            )
            assert recording_response.status_code == status.HTTP_201_CREATED
            loan_id = recording_response.json()["data"]["id"]

            first_return = client.patch(
                url=f"{RECORDING_LOAN_URL}{loan_id}/return",
                headers=member_auth_headers,
            )
            assert first_return.status_code == status.HTTP_200_OK

            second_return = client.patch(
                url=f"{RECORDING_LOAN_URL}{loan_id}/return",
                headers=member_auth_headers,
            )

            assert second_return.status_code == status.HTTP_409_CONFLICT
            assert second_return.json()["message"] == "Loan has already been returned."
