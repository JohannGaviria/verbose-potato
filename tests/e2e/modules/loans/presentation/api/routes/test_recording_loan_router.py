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


class TestRecordingLoan:
    class TestSuccess:
        def test_should_return_created_when_loan_data_is_valid(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()

            response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_201_CREATED

        def test_should_return_created_loan_data_when_registration_succeeds(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()

            response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_201_CREATED

            body = response.json()
            assert body["status"] == "success"
            assert body["message"] == "Loan registered successfully."

            data = body["data"]
            assert isinstance(UUID(data["id"]), UUID)
            assert isinstance(UUID(data["member_id"]), UUID)
            assert data["book_id"] == book["id"]
            assert data["status"] == "ACTIVE"
            assert data["loaned_at"] is not None
            assert data["returned_at"] is None

        def test_should_decrease_available_copies_and_invalidate_catalog_cache(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book(total_copies=1)

            catalog_before = client.get(
                url=GET_BOOK_CATALOG_URL,
                headers=member_auth_headers,
                params={"isbn": book["isbn"]},
            )
            assert catalog_before.status_code == status.HTTP_200_OK
            assert catalog_before.json()["data"]["items"][0]["available_copies"] == 1

            response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_201_CREATED

            catalog_after = client.get(
                url=GET_BOOK_CATALOG_URL,
                headers=member_auth_headers,
                params={"isbn": book["isbn"]},
            )
            assert catalog_after.status_code == status.HTTP_200_OK
            assert catalog_after.json()["data"]["items"][0]["available_copies"] == 0

    class TestUnauthorized:
        def test_should_return_unauthorized_when_token_is_missing(
            self,
            client: TestClient,
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()

            response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        def test_should_return_bad_request_when_token_is_invalid(
            self,
            client: TestClient,
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()

            response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers={"Authorization": "Bearer invalid-token"},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    class TestForbidden:
        def test_should_return_forbidden_when_user_is_not_a_member(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book()

            response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_403_FORBIDDEN

    class TestNotFound:
        def test_should_return_not_found_when_book_does_not_exist(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
        ) -> None:
            response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": str(uuid4())},
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json()["message"] == "Book cannot be found."

    class TestConflict:
        def test_should_return_conflict_when_member_already_has_active_loan_for_book(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book(total_copies=2)

            first_response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=member_auth_headers,
            )
            assert first_response.status_code == status.HTTP_201_CREATED

            second_response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=member_auth_headers,
            )

            assert second_response.status_code == status.HTTP_409_CONFLICT
            assert (
                second_response.json()["message"] == "Member already has active loan."
            )

        def test_should_return_conflict_when_book_has_no_available_copies(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_member_headers: RegisterMemberHeadersFactory,
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            book = register_loan_book(total_copies=1)

            first_response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=member_auth_headers,
            )
            assert first_response.status_code == status.HTTP_201_CREATED

            second_response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": book["id"]},
                headers=register_member_headers(),
            )

            assert second_response.status_code == status.HTTP_409_CONFLICT
            assert second_response.json()["message"] == "Book not available."

        def test_should_return_conflict_when_member_exceeds_maximum_active_loans(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
            register_loan_book: RegisterLoanBookFactory,
        ) -> None:
            for _ in range(5):
                book = register_loan_book()
                response = client.post(
                    url=RECORDING_LOAN_URL,
                    json={"book_id": book["id"]},
                    headers=member_auth_headers,
                )
                assert response.status_code == status.HTTP_201_CREATED

            sixth_book = register_loan_book()

            response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": sixth_book["id"]},
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_409_CONFLICT
            assert response.json()["message"] == "Maximum active loans exceeded."

    class TestUnprocessableEntity:
        def test_should_return_unprocessable_entity_when_book_id_is_missing(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
        ) -> None:
            response = client.post(
                url=RECORDING_LOAN_URL,
                json={},
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        def test_should_return_unprocessable_entity_when_book_id_is_malformed(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
        ) -> None:
            response = client.post(
                url=RECORDING_LOAN_URL,
                json={"book_id": "not-a-uuid"},
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        def test_should_return_unprocessable_entity_when_request_body_is_empty(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
        ) -> None:
            response = client.post(
                url=RECORDING_LOAN_URL,
                json=None,
                headers=member_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
