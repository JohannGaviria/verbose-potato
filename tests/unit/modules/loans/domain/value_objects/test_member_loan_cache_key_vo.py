from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from src.modules.loans.domain.value_objects.member_loan_cache_key_vo import (
    MemberLoanCacheKeyVO,
)
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO

_MEMBER_ID = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
_OTHER_MEMBER_ID = UUID("4fa85f64-5717-4562-b3fc-2c963f66afa6")


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
