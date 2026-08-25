from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from src.modules.books.domain.enums.book_catalog_sort_by_enum import (
    BookCatalogSortByEnum,
)
from src.modules.books.domain.exceptions.book_exception import (
    InvalidBookCatalogQueryException,
)
from src.modules.books.domain.value_objects.author_vo import AuthorVO
from src.modules.books.domain.value_objects.book_catalog_query_vo import (
    BookCatalogQueryVO,
)
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.shared.domain.enums.sort_order_enum import SortOrderEnum

VALID_ISBN_13 = "9780306406157"

_DEFAULTS: dict[str, Any] = {
    "title": None,
    "author": None,
    "isbn": None,
    "is_available": None,
    "sort_by": None,
    "sort_order": None,
    "page": 1,
    "page_size": 20,
}


def _build_query(**overrides: Any) -> BookCatalogQueryVO:
    data = {**_DEFAULTS, **overrides}
    return BookCatalogQueryVO(**data)


class TestBookCatalogQueryVO:
    def test_should_create_query_when_all_filters_are_none(self) -> None:
        query = _build_query()

        assert query.title is None
        assert query.author is None
        assert query.isbn is None
        assert query.is_available is None
        assert query.sort_by is None
        assert query.sort_order is None
        assert query.page == 1
        assert query.page_size == 20

    def test_should_create_query_when_all_filters_are_provided(self) -> None:
        title = TitleVO("Clean Code")
        author = AuthorVO("Robert Martin")
        isbn = IsbnVO(VALID_ISBN_13)

        query = _build_query(
            title=title,
            author=author,
            isbn=isbn,
            is_available=True,
            sort_by=BookCatalogSortByEnum.PUBLISHED_YEAR,
            sort_order=SortOrderEnum.DESC,
            page=3,
            page_size=50,
        )

        assert query.title == title
        assert query.author == author
        assert query.isbn == isbn
        assert query.is_available is True
        assert query.sort_by == BookCatalogSortByEnum.PUBLISHED_YEAR
        assert query.sort_order == SortOrderEnum.DESC
        assert query.page == 3
        assert query.page_size == 50

    @pytest.mark.parametrize("is_available", [True, False, None])
    def test_should_not_raise_exception_when_is_available_is_boolean_or_none(
        self, is_available: bool | None
    ) -> None:
        query = _build_query(is_available=is_available)

        assert query.is_available == is_available

    @pytest.mark.parametrize("is_available", ["yes", 1, 0, "true"])
    def test_should_raise_exception_when_is_available_is_not_a_boolean(
        self, is_available: Any
    ) -> None:
        with pytest.raises(InvalidBookCatalogQueryException):
            _build_query(is_available=is_available)

    @pytest.mark.parametrize(
        "sort_by",
        [BookCatalogSortByEnum.TITLE, BookCatalogSortByEnum.PUBLISHED_YEAR, None],
    )
    def test_should_not_raise_exception_when_sort_by_is_valid(
        self, sort_by: BookCatalogSortByEnum | None
    ) -> None:
        query = _build_query(sort_by=sort_by)

        assert query.sort_by == sort_by

    @pytest.mark.parametrize("sort_by", ["title", "published_year", 1])
    def test_should_raise_exception_when_sort_by_is_not_a_valid_enum_member(
        self, sort_by: Any
    ) -> None:
        with pytest.raises(InvalidBookCatalogQueryException):
            _build_query(sort_by=sort_by)

    @pytest.mark.parametrize(
        "sort_order", [SortOrderEnum.ASC, SortOrderEnum.DESC, None]
    )
    def test_should_not_raise_exception_when_sort_order_is_valid(
        self, sort_order: SortOrderEnum | None
    ) -> None:
        query = _build_query(sort_order=sort_order)

        assert query.sort_order == sort_order

    @pytest.mark.parametrize("sort_order", ["asc", "desc", 1])
    def test_should_raise_exception_when_sort_order_is_not_a_valid_enum_member(
        self, sort_order: Any
    ) -> None:
        with pytest.raises(InvalidBookCatalogQueryException):
            _build_query(sort_order=sort_order)

    @pytest.mark.parametrize("page", [1, 2, 100])
    def test_should_not_raise_exception_when_page_is_valid(self, page: int) -> None:
        query = _build_query(page=page)

        assert query.page == page

    @pytest.mark.parametrize("page", [0, -1, True, False, "1", None, 1.5])
    def test_should_raise_exception_when_page_is_invalid(self, page: Any) -> None:
        with pytest.raises(InvalidBookCatalogQueryException):
            _build_query(page=page)

    @pytest.mark.parametrize("page_size", [1, 20, 100])
    def test_should_not_raise_exception_when_page_size_is_valid(
        self, page_size: int
    ) -> None:
        query = _build_query(page_size=page_size)

        assert query.page_size == page_size

    @pytest.mark.parametrize(
        "page_size", [0, -1, True, False, "20", None, 1.5, 101, 1000]
    )
    def test_should_raise_exception_when_page_size_is_invalid(
        self, page_size: Any
    ) -> None:
        with pytest.raises(InvalidBookCatalogQueryException):
            _build_query(page_size=page_size)

    def test_should_raise_exception_when_attempting_to_modify_query(self) -> None:
        query = _build_query()

        with pytest.raises(FrozenInstanceError):
            query.page = 2  # type: ignore[misc]

    def test_should_be_equal_when_queries_have_same_values(self) -> None:
        first = _build_query(page=2, page_size=10)
        second = _build_query(page=2, page_size=10)

        assert first == second

    def test_should_not_be_equal_when_queries_have_different_values(self) -> None:
        first = _build_query(page=1)
        second = _build_query(page=2)

        assert first != second
