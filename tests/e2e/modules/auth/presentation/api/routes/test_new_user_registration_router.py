import asyncio
from datetime import datetime
from typing import Any
from uuid import UUID

import pytest
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings
from src.modules.auth.infrastructure.persistence.models.user_model import UserModel

pytestmark = [pytest.mark.e2e, pytest.mark.db]

REGISTER_URL = "/api/v1/auth/register"


def _valid_payload(faker: Faker) -> dict[str, Any]:
    """Builds a registration payload that satisfies every validation rule."""
    return {
        "name": faker.name(),
        "email": faker.email(),
        "password": faker.password(
            length=16,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        ),
    }


async def _fetch_stored_password_hash(email: str) -> str | None:
    """Reads the password hash persisted for a given email, straight from the database."""
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                select(UserModel.password).where(UserModel.email == email)
            )
            row = result.first()
            return row[0] if row else None
    finally:
        await engine.dispose()


class TestNewUserRegistration:
    class TestSuccess:
        def test_should_return_created_when_registration_data_is_valid(
            self, client: TestClient, faker: Faker
        ) -> None:
            payload = _valid_payload(faker)

            response = client.post(url=REGISTER_URL, json=payload)

            assert response.status_code == status.HTTP_201_CREATED

        def test_should_return_created_user_data_when_registration_succeeds(
            self, client: TestClient, faker: Faker
        ) -> None:
            payload = _valid_payload(faker)

            response = client.post(url=REGISTER_URL, json=payload)

            body = response.json()
            assert body["status"] == "success"
            assert body["message"] == "User registered successfully."

            data = body["data"]
            assert UUID(data["id"])
            assert data["name"] == payload["name"]
            assert data["email"] == payload["email"]
            assert data["role"] == "MEMBER"
            assert datetime.fromisoformat(data["created_at"])
            assert datetime.fromisoformat(data["updated_at"])
            assert "password" not in data

        def test_should_assign_member_role_automatically_when_user_registers(
            self, client: TestClient, faker: Faker
        ) -> None:
            payload = _valid_payload(faker)

            response = client.post(url=REGISTER_URL, json=payload)

            assert response.json()["data"]["role"] == "MEMBER"

        def test_should_store_password_hashed_with_argon2_when_user_registers(
            self, client: TestClient, faker: Faker
        ) -> None:
            payload = _valid_payload(faker)

            response = client.post(url=REGISTER_URL, json=payload)
            assert response.status_code == status.HTTP_201_CREATED

            stored_hash = asyncio.run(_fetch_stored_password_hash(payload["email"]))

            assert stored_hash is not None
            assert stored_hash != payload["password"]
            assert stored_hash.startswith("$argon2")

    class TestInvalidFormat:
        @pytest.mark.parametrize("name", ["", "ab", "a" * 101])
        def test_should_return_bad_request_when_name_format_is_invalid(
            self, client: TestClient, faker: Faker, name: str
        ) -> None:
            payload = _valid_payload(faker)
            payload["name"] = name

            response = client.post(url=REGISTER_URL, json=payload)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize(
            "email", ["", "test", "test@", "@gmail.com", "test.com"]
        )
        def test_should_return_bad_request_when_email_format_is_invalid(
            self, client: TestClient, faker: Faker, email: str
        ) -> None:
            payload = _valid_payload(faker)
            payload["email"] = email

            response = client.post(url=REGISTER_URL, json=payload)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize(
            "password",
            [
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
            payload = _valid_payload(faker)
            payload["password"] = password

            response = client.post(url=REGISTER_URL, json=payload)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        def test_should_not_persist_user_when_registration_data_is_invalid(
            self, client: TestClient, faker: Faker
        ) -> None:
            payload = _valid_payload(faker)
            payload["name"] = ""

            response = client.post(url=REGISTER_URL, json=payload)
            assert response.status_code == status.HTTP_400_BAD_REQUEST

            stored_hash = asyncio.run(_fetch_stored_password_hash(payload["email"]))
            assert stored_hash is None

    class TestConflict:
        def test_should_return_conflict_when_email_is_already_registered(
            self, client: TestClient, faker: Faker
        ) -> None:
            payload = _valid_payload(faker)

            first_response = client.post(url=REGISTER_URL, json=payload)
            assert first_response.status_code == status.HTTP_201_CREATED

            second_payload = _valid_payload(faker)
            second_payload["email"] = payload["email"]

            response = client.post(url=REGISTER_URL, json=second_payload)

            assert response.status_code == status.HTTP_409_CONFLICT
            assert response.json()["status"] == "error"

    class TestUnprocessableEntity:
        @pytest.mark.parametrize("missing_field", ["name", "email", "password"])
        def test_should_return_unprocessable_entity_when_required_field_is_missing(
            self, client: TestClient, faker: Faker, missing_field: str
        ) -> None:
            payload = _valid_payload(faker)
            del payload[missing_field]

            response = client.post(url=REGISTER_URL, json=payload)

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        @pytest.mark.parametrize("malformed_field", ["name", "email", "password"])
        def test_should_return_unprocessable_entity_when_field_has_wrong_type(
            self, client: TestClient, faker: Faker, malformed_field: str
        ) -> None:
            payload = _valid_payload(faker)
            payload[malformed_field] = 12345

            response = client.post(url=REGISTER_URL, json=payload)

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_body_is_empty(
            self, client: TestClient
        ) -> None:
            response = client.post(url=REGISTER_URL, json={})

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        def test_should_return_unprocessable_entity_when_no_body_is_sent(
            self, client: TestClient
        ) -> None:
            response = client.post(url=REGISTER_URL)

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
