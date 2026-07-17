from dataclasses import FrozenInstanceError

import pytest

from src.shared.domain.exceptions.cache_exception import InvalidCacheKeyException
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO


class TestCacheKeyVO:
    @pytest.mark.parametrize(
        "key",
        [
            "cache:user:123",
            "cache:session:abc:def",
            "cache:book_catalog:42",
            "cache:a:b",
        ],
    )
    def test_should_create_cache_key_when_key_matches_pattern(self, key: str) -> None:
        cache_key = CacheKeyVO(key=key)

        assert cache_key.key == key
        assert cache_key.value() == key

    def test_should_raise_exception_when_key_is_none(self) -> None:
        with pytest.raises(InvalidCacheKeyException):
            CacheKeyVO(key=None)  # type: ignore[arg-type]

    def test_should_raise_exception_when_key_is_not_a_string(self) -> None:
        with pytest.raises(InvalidCacheKeyException):
            CacheKeyVO(key=123)  # type: ignore[arg-type]

    def test_should_raise_exception_when_key_is_empty(self) -> None:
        with pytest.raises(InvalidCacheKeyException):
            CacheKeyVO(key="")

    def test_should_raise_exception_when_key_is_only_whitespace(self) -> None:
        with pytest.raises(InvalidCacheKeyException):
            CacheKeyVO(key="   ")

    @pytest.mark.parametrize(
        "key",
        [
            "user:123",
            "cache:user",
            "cache::123",
            "cache:user:",
            "cache: user:123",
            "not-a-cache-key",
        ],
    )
    def test_should_raise_exception_when_key_does_not_match_pattern(
        self, key: str
    ) -> None:
        with pytest.raises(InvalidCacheKeyException):
            CacheKeyVO(key=key)

    def test_should_raise_exception_when_key_is_longer_than_255_characters(
        self,
    ) -> None:
        long_key = "cache:user:" + ("a" * 250)

        with pytest.raises(InvalidCacheKeyException):
            CacheKeyVO(key=long_key)

    def test_should_create_cache_key_when_key_is_exactly_255_characters(self) -> None:
        prefix = "cache:user:"
        key = prefix + ("a" * (255 - len(prefix)))

        cache_key = CacheKeyVO(key=key)

        assert len(cache_key.key) == 255

    def test_should_be_immutable_when_created(self) -> None:
        cache_key = CacheKeyVO(key="cache:user:123")

        with pytest.raises(FrozenInstanceError):
            cache_key.key = "cache:user:456"  # type: ignore[misc]

    def test_should_be_equal_when_keys_have_same_value(self) -> None:
        first = CacheKeyVO(key="cache:user:123")
        second = CacheKeyVO(key="cache:user:123")

        assert first == second

    def test_should_not_be_equal_when_keys_have_different_value(self) -> None:
        first = CacheKeyVO(key="cache:user:123")
        second = CacheKeyVO(key="cache:user:456")

        assert first != second
