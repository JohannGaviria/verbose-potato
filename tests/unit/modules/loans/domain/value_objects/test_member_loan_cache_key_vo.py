from dataclasses import FrozenInstanceError
from typing import Any
from uuid import UUID

import pytest

from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.value_objects.member_loan_cache_key_vo import (
    MemberLoanCacheKeyVO,
)
from src.modules.loans.domain.value_objects.member_loan_query_vo import (
    MemberLoanQueryVO,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO

_MEMBER_ID = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
_OTHER_MEMBER_ID = UUID("4fa85f64-5717-4562-b3fc-2c963f66afa6")

_DEFAULT: dict[str, Any] = {
    "status": None,
    "sort_by": None,
    "sort_order": None,
    "page": 1,
    "page_size": 20,
}


def _build_query(**overrides: Any) -> MemberLoanQueryVO:
    data = {**_DEFAULT, **overrides}
    return MemberLoanQueryVO(**data)


class TestMemberLoanCacheKeyVO:
    def test_should_return_member_pattern_when_for_member_is_called(self) -> None:
        cache_key = MemberLoanCacheKeyVO.for_member(_MEMBER_ID)

        assert cache_key.key == f"cache:loans:member:{_MEMBER_ID}"
        assert cache_key.value() == f"cache:loans:member:{_MEMBER_ID}"

    def test_should_be_a_cache_key_vo_instance(self) -> None:
        cache_key = MemberLoanCacheKeyVO.for_member(_MEMBER_ID)

        assert isinstance(cache_key, CacheKeyVO)

    def test_should_be_equal_when_member_is_the_same(self) -> None:
        first_key = MemberLoanCacheKeyVO.for_member(_MEMBER_ID)
        second_key = MemberLoanCacheKeyVO.for_member(_MEMBER_ID)

        assert first_key == second_key

    def test_should_not_be_equal_when_member_is_different(self) -> None:
        first_key = MemberLoanCacheKeyVO.for_member(_MEMBER_ID)
        second_key = MemberLoanCacheKeyVO.for_member(_OTHER_MEMBER_ID)

        assert first_key != second_key

    def test_should_be_immutable_when_created(self) -> None:
        cache_key = MemberLoanCacheKeyVO.for_member(_MEMBER_ID)

        with pytest.raises(FrozenInstanceError):
            cache_key.key = "cache:loans:member:other"  # type: ignore[misc]

    def test_should_support_namespace_variants(self) -> None:
        pattern = MemberLoanCacheKeyVO.for_member(_MEMBER_ID).value()

        variants = [f"{pattern}:hash-1", f"{pattern}:hash-2"]

        assert len(variants) == 2

    def test_should_build_member_filter_key_from_filters(self) -> None:
        query = _build_query(
            status=LoanStatusEnum.ACTIVE,
            sort_by=LoanSortByEnum.LOANED_AT,
            sort_order=SortOrderEnum.DESC,
            page=2,
            page_size=10,
        )

        cache_key = MemberLoanCacheKeyVO.from_filters(_MEMBER_ID, query)

        assert cache_key.key.startswith(f"cache:loans:member:{_MEMBER_ID}:")
        assert cache_key.value() == cache_key.key

    def test_from_filters_should_be_a_cache_key_vo_instance(self) -> None:
        cache_key = MemberLoanCacheKeyVO.from_filters(_MEMBER_ID, _build_query())

        assert isinstance(cache_key, CacheKeyVO)

    def test_from_filters_should_be_equal_for_same_member_and_filters(self) -> None:
        first = MemberLoanCacheKeyVO.from_filters(_MEMBER_ID, _build_query())
        second = MemberLoanCacheKeyVO.from_filters(_MEMBER_ID, _build_query())

        assert first == second

    def test_from_filters_should_differ_when_filters_change(self) -> None:
        plain = MemberLoanCacheKeyVO.from_filters(_MEMBER_ID, _build_query())
        filtered = MemberLoanCacheKeyVO.from_filters(
            _MEMBER_ID,
            _build_query(status=LoanStatusEnum.ACTIVE),
        )

        assert plain != filtered

    def test_from_filters_should_differ_when_member_changes(self) -> None:
        first = MemberLoanCacheKeyVO.from_filters(_MEMBER_ID, _build_query())
        second = MemberLoanCacheKeyVO.from_filters(_OTHER_MEMBER_ID, _build_query())

        assert first != second

    def test_from_filters_key_should_match_validation_pattern(self) -> None:
        cache_key = MemberLoanCacheKeyVO.from_filters(_MEMBER_ID, _build_query())

        assert cache_key.key == cache_key.value()
