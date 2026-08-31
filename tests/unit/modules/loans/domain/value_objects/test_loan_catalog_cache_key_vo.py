from dataclasses import FrozenInstanceError
from typing import Any
from uuid import uuid4

import pytest

from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.value_objects.loan_catalog_cache_key_vo import (
    LoanCatalogCacheKeyVO,
)
from src.modules.loans.domain.value_objects.loan_catalog_query_vo import (
    LoanCatalogQueryVO,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO

_DEFAULT: dict[str, Any] = {
    "member_id": None,
    "book_id": None,
    "status": None,
    "sort_by": None,
    "sort_order": None,
    "page": 1,
    "page_size": 20,
}


def _build_query(**overrides: Any) -> LoanCatalogQueryVO:
    data = {**_DEFAULT, **overrides}
    return LoanCatalogQueryVO(**data)


class TestLoanCatalogCacheKeyVO:
    def test_should_return_base_pattern_when_pattern_is_called(self) -> None:
        cache_key = LoanCatalogCacheKeyVO.pattern()

        assert cache_key.key == "cache:loans:catalog"
        assert cache_key.value() == "cache:loans:catalog"

    def test_should_be_a_cache_key_vo_instance(self) -> None:
        cache_key = LoanCatalogCacheKeyVO.pattern()

        assert isinstance(cache_key, CacheKeyVO)

    def test_should_be_equal_when_pattern_is_called_multiple_times(self) -> None:
        first_key = LoanCatalogCacheKeyVO.pattern()
        second_key = LoanCatalogCacheKeyVO.pattern()

        assert first_key == second_key

    def test_should_be_immutable_when_created(self) -> None:
        cache_key = LoanCatalogCacheKeyVO.pattern()

        with pytest.raises(FrozenInstanceError):
            cache_key.key = "cache:loans:catalog:other"  # type: ignore[misc]

    def test_should_support_namespace_variants(self) -> None:
        pattern = LoanCatalogCacheKeyVO.pattern().value()

        variants = [f"{pattern}:hash-1", f"{pattern}:hash-2", f"{pattern}:hash-3"]

        assert len(variants) == 3

    def test_should_generate_key_with_prefix_and_hash(self) -> None:
        query = _build_query()

        cache_key = LoanCatalogCacheKeyVO.from_filters(query)

        assert cache_key.value().startswith("cache:loans:catalog:")

    def test_should_generate_same_key_for_equivalent_queries(self) -> None:
        first_key = LoanCatalogCacheKeyVO.from_filters(_build_query())
        second_key = LoanCatalogCacheKeyVO.from_filters(_build_query())

        assert first_key == second_key

    def test_should_generate_different_key_when_filters_differ(self) -> None:
        first_key = LoanCatalogCacheKeyVO.from_filters(
            _build_query(status=LoanStatusEnum.ACTIVE)
        )
        second_key = LoanCatalogCacheKeyVO.from_filters(
            _build_query(status=LoanStatusEnum.RETURNED)
        )

        assert first_key != second_key

    def test_should_generate_different_key_when_member_id_differs(self) -> None:
        first_key = LoanCatalogCacheKeyVO.from_filters(_build_query(member_id=uuid4()))
        second_key = LoanCatalogCacheKeyVO.from_filters(_build_query(member_id=uuid4()))

        assert first_key != second_key

    def test_should_generate_different_key_when_pagination_differs(self) -> None:
        first_key = LoanCatalogCacheKeyVO.from_filters(
            _build_query(page=1, page_size=10)
        )
        second_key = LoanCatalogCacheKeyVO.from_filters(
            _build_query(page=2, page_size=10)
        )

        assert first_key != second_key

    def test_should_include_all_filters_in_the_key_canonical(self) -> None:
        full_query = _build_query(
            member_id=uuid4(),
            book_id=uuid4(),
            status=LoanStatusEnum.RETURNED,
            sort_by=LoanSortByEnum.RETURNED_AT,
            sort_order=SortOrderEnum.DESC,
            page=3,
            page_size=50,
        )

        cache_key = LoanCatalogCacheKeyVO.from_filters(full_query)

        assert cache_key.value().startswith("cache:loans:catalog:")
