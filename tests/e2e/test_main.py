import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.config import settings
from src.shared.presentation.api.middleware.correlation_id_middleware import (
    CorrelationIdMiddleware,
)

pytestmark = [pytest.mark.e2e, pytest.mark.db]


class TestRootEndpoint:
    def test_should_return_welcome_message_when_root_is_requested(
        self, client: TestClient
    ) -> None:
        response = client.get(url="/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "message": (
                f"Welcome to the {settings.APP_NAME}, version {settings.APP_VERSION}!"
            )
        }

    def test_should_include_correlation_id_header_when_root_is_requested(
        self, client: TestClient
    ) -> None:
        response = client.get(url="/")

        assert CorrelationIdMiddleware.HEADER_NAME in response.headers


class TestHealthCheckEndpoint:
    def test_should_return_healthy_when_database_and_redis_are_available(
        self, client: TestClient
    ) -> None:
        response = client.get(url="/health")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["status"] == "healthy"
        assert body["database"] is True
        assert body["redis"] is True

    def test_should_include_correlation_id_header_when_health_is_requested(
        self, client: TestClient
    ) -> None:
        response = client.get(url="/health")

        assert CorrelationIdMiddleware.HEADER_NAME in response.headers

    def test_should_preserve_client_correlation_id_when_provided(
        self, client: TestClient
    ) -> None:
        given_id = "e2e-health-check-id"

        response = client.get(
            url="/health", headers={CorrelationIdMiddleware.HEADER_NAME: given_id}
        )

        assert response.headers[CorrelationIdMiddleware.HEADER_NAME] == given_id


class TestCORSConfiguration:
    def test_should_allow_configured_origin_when_preflight_request_is_made(
        self, client: TestClient
    ) -> None:
        allowed_origin = settings.CORS_ALLOW_ORIGINS.split(",")[0].strip()

        response = client.options(
            url="/",
            headers={
                "Origin": allowed_origin,
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.headers.get("access-control-allow-origin") == allowed_origin


class TestApplicationMetadata:
    def test_should_expose_openapi_schema_when_requested(
        self, client: TestClient
    ) -> None:
        response = client.get("/openapi.json")

        assert response.status_code == status.HTTP_200_OK
        schema = response.json()
        assert schema["info"]["title"] == settings.APP_NAME
        assert schema["info"]["version"] == settings.APP_VERSION
