from typing import Any
from uuid import UUID

import jwt
import pytest
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient

from src.config import settings

pytestmark = [pytest.mark.e2e, pytest.mark.db]

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"


def _valid_password(faker: Faker) -> str:
    """Builds a password that satisfies every complexity rule."""
    return faker.password(
        length=16,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )


def _valid_registration_payload(faker: Faker) -> dict[str, Any]:
    """Builds a registration payload that satisfies every validation rule."""
    return {
        "name": faker.name(),
        "email": faker.email(),
        "password": _valid_password(faker),
    }


def _register_user(client: TestClient, faker: Faker) -> dict[str, Any]:
    """Registers a new user through the API and returns the payload used."""
    payload = _valid_registration_payload(faker)

    response = client.post(url=REGISTER_URL, json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    return payload


class TestLogin:
    class TestSuccess:
        def test_should_return_ok_when_credentials_are_valid(
            self, client: TestClient, faker: Faker
        ) -> None:
            registered_user = _register_user(client, faker)

            response = client.post(
                url=LOGIN_URL,
                json={
                    "email": registered_user["email"],
                    "password": registered_user["password"],
                },
            )

            assert response.status_code == status.HTTP_200_OK

        def test_should_return_user_and_access_token_data_when_login_succeeds(
            self, client: TestClient, faker: Faker
        ) -> None:
            registered_user = _register_user(client, faker)

            response = client.post(
                url=LOGIN_URL,
                json={
                    "email": registered_user["email"],
                    "password": registered_user["password"],
                },
            )

            body = response.json()
            assert body["status"] == "success"
            assert body["message"] == "Login successful."

            user_data = body["data"]["user"]
            assert UUID(user_data["id"])
            assert user_data["name"] == registered_user["name"]
            assert user_data["email"] == registered_user["email"]
            assert user_data["role"] == "MEMBER"

            access_token_data = body["data"]["access_token"]
            assert access_token_data["access_token"]
            assert access_token_data["token_type"] == "Bearer"
            assert (
                access_token_data["expires_in"] == settings.JWT_ACCESS_TOKEN_EXPIRES_IN
            )

        def test_should_return_access_token_containing_correct_claims_when_login_succeeds(
            self, client: TestClient, faker: Faker
        ) -> None:
            registered_user = _register_user(client, faker)

            response = client.post(
                url=LOGIN_URL,
                json={
                    "email": registered_user["email"],
                    "password": registered_user["password"],
                },
            )
            body = response.json()

            user_id = body["data"]["user"]["id"]
            access_token = body["data"]["access_token"]["access_token"]

            decoded = jwt.decode(
                access_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )

            assert UUID(decoded["jti"])
            assert decoded["sub"] == user_id
            assert decoded["role"] == "MEMBER"

        def test_should_allow_login_with_different_registered_users(
            self, client: TestClient, faker: Faker
        ) -> None:
            first_user = _register_user(client, faker)
            second_user = _register_user(client, faker)

            first_response = client.post(
                url=LOGIN_URL,
                json={
                    "email": first_user["email"],
                    "password": first_user["password"],
                },
            )
            second_response = client.post(
                url=LOGIN_URL,
                json={
                    "email": second_user["email"],
                    "password": second_user["password"],
                },
            )

            assert first_response.status_code == status.HTTP_200_OK
            assert second_response.status_code == status.HTTP_200_OK
            assert (
                first_response.json()["data"]["user"]["id"]
                != second_response.json()["data"]["user"]["id"]
            )

    class TestUnauthorized:
        def test_should_return_unauthorized_when_email_is_not_registered(
            self, client: TestClient, faker: Faker
        ) -> None:
            response = client.post(
                url=LOGIN_URL,
                json={
                    "email": faker.email(),
                    "password": _valid_password(faker),
                },
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["status"] == "error"

        def test_should_return_unauthorized_when_password_is_incorrect(
            self, client: TestClient, faker: Faker
        ) -> None:
            registered_user = _register_user(client, faker)
            wrong_password = _valid_password(faker)
            while wrong_password == registered_user["password"]:
                wrong_password = _valid_password(faker)

            response = client.post(
                url=LOGIN_URL,
                json={
                    "email": registered_user["email"],
                    "password": wrong_password,
                },
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["status"] == "error"

        def test_should_not_reveal_whether_email_exists_in_error_message(
            self, client: TestClient, faker: Faker
        ) -> None:
            registered_user = _register_user(client, faker)
            wrong_password = _valid_password(faker)
            while wrong_password == registered_user["password"]:
                wrong_password = _valid_password(faker)

            unknown_email_response = client.post(
                url=LOGIN_URL,
                json={
                    "email": faker.email(),
                    "password": _valid_password(faker),
                },
            )
            wrong_password_response = client.post(
                url=LOGIN_URL,
                json={
                    "email": registered_user["email"],
                    "password": wrong_password,
                },
            )

            assert (
                unknown_email_response.json()["message"]
                == wrong_password_response.json()["message"]
            )

    class TestInvalidFormat:
        @pytest.mark.parametrize(
            "email", ["", "test", "test@", "@gmail.com", "test.com"]
        )
        def test_should_return_bad_request_when_email_format_is_invalid(
            self, client: TestClient, faker: Faker, email: str
        ) -> None:
            response = client.post(
                url=LOGIN_URL,
                json={"email": email, "password": _valid_password(faker)},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize(
            "password",
            [
                "",
                "Aa1!",
                "Aa1!" * 5,
                "password1!",
                "PASSWORD1!",
                "Password!",
                "Password1",
            ],
        )
        def test_should_return_bad_request_when_password_format_is_invalid(
            self, client: TestClient, faker: Faker, password: str
        ) -> None:
            response = client.post(
                url=LOGIN_URL,
                json={"email": faker.email(), "password": password},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        def test_should_return_bad_request_when_password_format_is_invalid_even_for_a_registered_user(
            self, client: TestClient, faker: Faker
        ) -> None:
            registered_user = _register_user(client, faker)

            response = client.post(
                url=LOGIN_URL,
                json={"email": registered_user["email"], "password": "short"},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

    class TestUnprocessableEntity:
        @pytest.mark.parametrize("missing_field", ["email", "password"])
        def test_should_return_unprocessable_entity_when_required_field_is_missing(
            self, client: TestClient, faker: Faker, missing_field: str
        ) -> None:
            payload = {"email": faker.email(), "password": _valid_password(faker)}
            del payload[missing_field]

            response = client.post(url=LOGIN_URL, json=payload)

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        @pytest.mark.parametrize("malformed_field", ["email", "password"])
        def test_should_return_unprocessable_entity_when_field_has_wrong_type(
            self, client: TestClient, faker: Faker, malformed_field: str
        ) -> None:
            payload = {"email": faker.email(), "password": _valid_password(faker)}
            payload[malformed_field] = 12345

            response = client.post(url=LOGIN_URL, json=payload)

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_body_is_empty(
            self, client: TestClient
        ) -> None:
            response = client.post(url=LOGIN_URL, json={})

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        def test_should_return_unprocessable_entity_when_no_body_is_sent(
            self, client: TestClient
        ) -> None:
            response = client.post(url=LOGIN_URL)

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
