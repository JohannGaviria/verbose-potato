import re
from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from src.modules.books.domain.enums.book_catalog_sort_by_enum import (
    BookCatalogSortByEnum,
)
from src.modules.books.domain.value_objects.author_vo import AuthorVO
from src.modules.books.domain.value_objects.book_catalog_cache_key_vo import (
    BookCatalogCacheKeyVO,
)
from src.modules.books.domain.value_objects.book_catalog_query_vo import (
    BookCatalogQueryVO,
)
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO

VALID_ISBN_13 = "9780306406157"
OTHER_VALID_ISBN_13 = "9780132350884"

_HASHED_KEY_PATTERN = re.compile(r"^cache:books:catalog:[0-9a-f]{64}$")

_DEFAULTS: dict[str, Any] = {
    "title": TitleVO("Clean Code"),
    "author": AuthorVO("Robert Martin"),
    "isbn": IsbnVO(VALID_ISBN_13),
    "is_available": True,
    "sort_by": BookCatalogSortByEnum.TITLE,
    "sort_order": SortOrderEnum.ASC,
    "page": 1,
    "page_size": 20,
}


def _build_query(**overrides: Any) -> BookCatalogQueryVO:
    data = {**_DEFAULTS, **overrides}
    return BookCatalogQueryVO(**data)


class TestBookCatalogCacheKeyVO:
    def test_should_return_base_pattern_when_pattern_is_called(self) -> None:
        cache_key = BookCatalogCacheKeyVO.pattern()

        assert cache_key.key == "cache:books:catalog"
        assert cache_key.value() == "cache:books:catalog"

    def test_should_be_a_cache_key_vo_instance(self) -> None:
        cache_key = BookCatalogCacheKeyVO.pattern()

        assert isinstance(cache_key, CacheKeyVO)

    def test_should_create_hashed_key_matching_pattern_when_from_filters_is_called(
        self,
    ) -> None:
        query = _build_query()

        cache_key = BookCatalogCacheKeyVO.from_filters(query)

        assert _HASHED_KEY_PATTERN.match(cache_key.value())

    def test_should_create_hashed_key_when_all_filters_are_none(self) -> None:
        query = BookCatalogQueryVO(
            title=None,
            author=None,
            isbn=None,
            is_available=None,
            sort_by=None,
            sort_order=None,
            page=1,
            page_size=20,
        )

        cache_key = BookCatalogCacheKeyVO.from_filters(query)

        assert _HASHED_KEY_PATTERN.match(cache_key.value())

    def test_should_return_same_key_when_filters_are_equivalent(self) -> None:
        first_query = _build_query()
        second_query = _build_query()

        first_key = BookCatalogCacheKeyVO.from_filters(first_query)
        second_key = BookCatalogCacheKeyVO.from_filters(second_query)

        assert first_key == second_key
        assert first_key.value() == second_key.value()

    @pytest.mark.parametrize(
        "overrides",
        [
            {"title": TitleVO("Other Title")},
            {"title": None},
            {"author": AuthorVO("Different Author")},
            {"author": None},
            {"isbn": IsbnVO(OTHER_VALID_ISBN_13)},
            {"isbn": None},
            {"is_available": False},
            {"is_available": None},
            {"sort_by": BookCatalogSortByEnum.PUBLISHED_YEAR},
            {"sort_by": None},
            {"sort_order": SortOrderEnum.DESC},
            {"sort_order": None},
            {"page": 2},
            {"page_size": 50},
        ],
    )
    def test_should_return_different_key_when_a_filter_changes(
        self, overrides: dict[str, Any]
    ) -> None:
        base_key = BookCatalogCacheKeyVO.from_filters(_build_query())
        other_key = BookCatalogCacheKeyVO.from_filters(_build_query(**overrides))

        assert base_key != other_key

    def test_should_be_immutable_when_created(self) -> None:
        cache_key = BookCatalogCacheKeyVO.pattern()

        with pytest.raises(FrozenInstanceError):
            cache_key.key = "cache:books:catalog:other"  # type: ignore[misc]
