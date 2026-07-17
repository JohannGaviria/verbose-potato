import structlog
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from src.shared.presentation.api.middleware.correlation_id_middleware import (
    CorrelationIdMiddleware,
)


def build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    @app.get(path="/ping")
    async def ping() -> dict:
        return {
            "correlation_id": structlog.contextvars.get_contextvars().get(
                "correlation_id"
            )
        }

    @app.get(path="/context-keys")
    async def context_keys() -> dict:
        return {"keys": sorted(structlog.contextvars.get_contextvars().keys())}

    return app


class TestCorrelationIdMiddleware:
    def test_should_add_correlation_id_header_when_not_provided(self) -> None:
        client = TestClient(build_app())

        response = client.get(url="/ping")

        assert response.status_code == status.HTTP_200_OK
        assert CorrelationIdMiddleware.HEADER_NAME in response.headers
        assert response.headers[CorrelationIdMiddleware.HEADER_NAME] != ""

    def test_should_preserve_correlation_id_when_provided_in_request(self) -> None:
        client = TestClient(build_app())
        given_id = "my-correlation-id-123"

        response = client.get(
            url="/ping", headers={CorrelationIdMiddleware.HEADER_NAME: given_id}
        )

        assert response.headers[CorrelationIdMiddleware.HEADER_NAME] == given_id

    def test_should_bind_correlation_id_to_response_body_when_read_from_contextvars(
        self,
    ) -> None:
        client = TestClient(build_app())
        given_id = "my-correlation-id-456"

        response = client.get(
            url="/ping", headers={CorrelationIdMiddleware.HEADER_NAME: given_id}
        )

        assert response.json()["correlation_id"] == given_id

    def test_should_generate_different_correlation_ids_across_requests(self) -> None:
        client = TestClient(build_app())

        first = client.get(url="/ping").headers[CorrelationIdMiddleware.HEADER_NAME]
        second = client.get(url="/ping").headers[CorrelationIdMiddleware.HEADER_NAME]

        assert first != second

    def test_should_expose_only_correlation_id_in_structlog_context(self) -> None:
        client = TestClient(build_app())

        response = client.get(
            url="/context-keys",
            headers={CorrelationIdMiddleware.HEADER_NAME: "my-correlation-id-789"},
        )

        assert response.json()["keys"] == ["correlation_id"]

    def test_should_use_the_new_correlation_id_when_second_request_arrives(
        self,
    ) -> None:
        client = TestClient(build_app())

        first = client.get(
            url="/ping", headers={CorrelationIdMiddleware.HEADER_NAME: "first-id"}
        )
        second = client.get(
            url="/ping", headers={CorrelationIdMiddleware.HEADER_NAME: "second-id"}
        )

        assert first.json()["correlation_id"] == "first-id"
        assert second.json()["correlation_id"] == "second-id"
