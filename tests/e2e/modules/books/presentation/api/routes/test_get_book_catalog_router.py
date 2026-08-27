from collections.abc import Callable
from math import ceil
from typing import Any
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.e2e, pytest.mark.db]

GET_BOOK_CATALOG_URL = "/api/v1/books/"
REGISTER_BOOK_URL = "/api/v1/books/register"

RegisterBookPayloadFactory = Callable[[], dict[str, Any]]


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


def _marker() -> str:
    """A unique-enough marker used to isolate a test's books from the rest of the catalog."""
    return f"CatalogE2E-{uuid4().hex[:10]}"


class TestGetBookCatalog:
    class TestSuccess:
        def test_should_return_ok_when_request_is_valid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.get(
                url=GET_BOOK_CATALOG_URL, headers=librarian_auth_headers
            )

            assert response.status_code == status.HTTP_200_OK

        def test_should_return_expected_envelope_and_default_pagination(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.get(
                url=GET_BOOK_CATALOG_URL, headers=librarian_auth_headers
            )

            body = response.json()
            assert body["status"] == "success"
            assert body["message"] == "Book catalog retrieved successfully."

            data = body["data"]
            assert isinstance(data["items"], list)
            assert data["page"] == 1
            assert data["page_size"] == 20
            assert data["total"] >= 1
            assert data["total_pages"] == ceil(data["total"] / data["page_size"])

            item = data["items"][0]
            assert {
                "id",
                "title",
                "isbn",
                "author",
                "published_year",
                "total_copies",
                "available_copies",
                "created_at",
                "updated_at",
            }.issubset(item.keys())

        def test_should_allow_member_to_browse_the_catalog(
            self,
            client: TestClient,
            member_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(url=GET_BOOK_CATALOG_URL, headers=member_auth_headers)

            assert response.status_code == status.HTTP_200_OK
            assert response.json()["status"] == "success"

        def test_should_filter_books_by_title(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            marker = _marker()
            book = _register_book(
                client,
                librarian_auth_headers,
                register_book_payload,
                title=f"Clean Architecture {marker}",
            )
            _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"title": marker},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert data["total"] == 1
            assert [item["id"] for item in data["items"]] == [book["id"]]

        def test_should_filter_books_by_title_case_insensitively(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            marker = _marker()
            book = _register_book(
                client,
                librarian_auth_headers,
                register_book_payload,
                title=f"Clean Architecture {marker}",
            )

            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"title": marker.lower()},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            assert data["total"] == 1
            assert data["items"][0]["id"] == book["id"]

        def test_should_filter_books_by_author(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            marker = _marker()
            book = _register_book(
                client,
                librarian_auth_headers,
                register_book_payload,
                author=f"Robert C. Martin {marker}",
            )
            _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"author": marker},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert data["total"] == 1
            assert [item["id"] for item in data["items"]] == [book["id"]]

        def test_should_filter_books_by_exact_isbn(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            book = _register_book(client, librarian_auth_headers, register_book_payload)
            _register_book(client, librarian_auth_headers, register_book_payload)

            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"isbn": book["isbn"]},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert data["total"] == 1
            assert data["items"][0]["id"] == book["id"]
            assert data["items"][0]["isbn"] == book["isbn"]

        def test_should_return_only_available_books_when_filter_is_true(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            marker = _marker()
            for _ in range(3):
                _register_book(
                    client,
                    librarian_auth_headers,
                    register_book_payload,
                    author=f"Available Author {marker}",
                )

            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"author": marker, "is_available": "true"},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert data["total"] == 3
            assert all(item["available_copies"] > 0 for item in data["items"])

        def test_should_sort_books_by_title_ascending(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            marker = _marker()
            full_titles = [
                f"{title} {marker}" for title in ("Charlie", "Alpha", "Bravo")
            ]
            for title in full_titles:
                _register_book(
                    client,
                    librarian_auth_headers,
                    register_book_payload,
                    title=title,
                    author=marker,
                )

            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"author": marker, "sort_by": "title", "sort_order": "asc"},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            returned_titles = [item["title"] for item in data["items"]]
            assert returned_titles == sorted(full_titles)

        def test_should_sort_books_by_title_descending(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            marker = _marker()
            full_titles = [
                f"{title} {marker}" for title in ("Charlie", "Alpha", "Bravo")
            ]
            for title in full_titles:
                _register_book(
                    client,
                    librarian_auth_headers,
                    register_book_payload,
                    title=title,
                    author=marker,
                )

            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"author": marker, "sort_by": "title", "sort_order": "desc"},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            returned_titles = [item["title"] for item in data["items"]]
            assert returned_titles == sorted(full_titles, reverse=True)

        def test_should_sort_books_by_published_year(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            marker = _marker()
            for year in (2005, 2020, 2012):
                _register_book(
                    client,
                    librarian_auth_headers,
                    register_book_payload,
                    author=marker,
                    published_year=year,
                )

            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={
                    "author": marker,
                    "sort_by": "published_year",
                    "sort_order": "desc",
                },
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            returned_years = [item["published_year"] for item in data["items"]]
            assert returned_years == [2020, 2012, 2005]

        def test_should_default_to_insertion_order_when_sort_by_is_not_provided(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            marker = _marker()
            first_book = _register_book(
                client, librarian_auth_headers, register_book_payload, author=marker
            )
            second_book = _register_book(
                client, librarian_auth_headers, register_book_payload, author=marker
            )

            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"author": marker},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            assert [item["id"] for item in data["items"]] == [
                first_book["id"],
                second_book["id"],
            ]

        def test_should_paginate_results_according_to_page_and_page_size(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            register_book_payload: RegisterBookPayloadFactory,
        ) -> None:
            marker = _marker()
            titles = ["Alpha", "Bravo", "Charlie", "Delta", "Echo"]
            for title in titles:
                _register_book(
                    client,
                    librarian_auth_headers,
                    register_book_payload,
                    title=f"{title} {marker}",
                    author=marker,
                )

            common_params: dict[str, Any] = {
                "author": marker,
                "sort_by": "title",
                "sort_order": "asc",
                "page_size": 2,
            }

            first_page = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={**common_params, "page": 1},
                headers=librarian_auth_headers,
            ).json()["data"]
            second_page = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={**common_params, "page": 2},
                headers=librarian_auth_headers,
            ).json()["data"]
            third_page = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={**common_params, "page": 3},
                headers=librarian_auth_headers,
            ).json()["data"]

            assert [item["title"] for item in first_page["items"]] == [
                f"Alpha {marker}",
                f"Bravo {marker}",
            ]
            assert [item["title"] for item in second_page["items"]] == [
                f"Charlie {marker}",
                f"Delta {marker}",
            ]
            assert [item["title"] for item in third_page["items"]] == [
                f"Echo {marker}",
            ]

            for page in (first_page, second_page, third_page):
                assert page["total"] == 5
                assert page["total_pages"] == 3
                assert page["page_size"] == 2

        def test_should_return_empty_items_when_no_books_match_filters(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"title": _marker()},
                headers=librarian_auth_headers,
            )

            data = response.json()["data"]
            assert response.status_code == status.HTTP_200_OK
            assert data["items"] == []
            assert data["total"] == 0
            assert data["total_pages"] == 0

    class TestUnauthorized:
        def test_should_return_unauthorized_when_no_token_is_provided(
            self, client: TestClient
        ) -> None:
            response = client.get(url=GET_BOOK_CATALOG_URL)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["status"] == "error"

        def test_should_return_bad_request_when_token_is_invalid(
            self, client: TestClient
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                headers={"Authorization": "Bearer not-a-real-token"},
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

    class TestBadRequest:
        @pytest.mark.parametrize("title", ["a", "ab"])
        def test_should_return_bad_request_when_title_filter_is_too_short(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            title: str,
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"title": title},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize("author", ["a", "ab"])
        def test_should_return_bad_request_when_author_filter_is_too_short(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            author: str,
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"author": author},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize("isbn", ["123", "9780306406158", "not-an-isbn"])
        def test_should_return_bad_request_when_isbn_filter_is_invalid(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            isbn: str,
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"isbn": isbn},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize("page", [0, -1])
        def test_should_return_bad_request_when_page_is_less_than_one(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            page: int,
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"page": page},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize("page_size", [0, -1])
        def test_should_return_bad_request_when_page_size_is_less_than_one(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            page_size: int,
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"page_size": page_size},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

        @pytest.mark.parametrize("page_size", [101, 1000])
        def test_should_return_bad_request_when_page_size_exceeds_maximum(
            self,
            client: TestClient,
            librarian_auth_headers: dict[str, str],
            page_size: int,
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"page_size": page_size},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["status"] == "error"

    class TestUnprocessableEntity:
        def test_should_return_unprocessable_entity_when_sort_by_is_invalid(
            self, client: TestClient, librarian_auth_headers: dict[str, str]
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"sort_by": "not-a-valid-field"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_sort_order_is_invalid(
            self, client: TestClient, librarian_auth_headers: dict[str, str]
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"sort_order": "not-a-valid-order"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_is_available_is_not_a_boolean(
            self, client: TestClient, librarian_auth_headers: dict[str, str]
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"is_available": "not-a-boolean"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_page_is_not_an_integer(
            self, client: TestClient, librarian_auth_headers: dict[str, str]
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"page": "not-a-number"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()

        def test_should_return_unprocessable_entity_when_page_size_is_not_an_integer(
            self, client: TestClient, librarian_auth_headers: dict[str, str]
        ) -> None:
            response = client.get(
                url=GET_BOOK_CATALOG_URL,
                params={"page_size": "not-a-number"},
                headers=librarian_auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert "detail" in response.json()
