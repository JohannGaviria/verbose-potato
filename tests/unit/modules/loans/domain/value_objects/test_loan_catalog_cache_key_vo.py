from dataclasses import FrozenInstanceError

import pytest

from src.modules.loans.domain.value_objects.loan_catalog_cache_key_vo import (
    LoanCatalogCacheKeyVO,
)
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO


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
