from dataclasses import FrozenInstanceError

import pytest

from src.shared.domain.exceptions.cache_exception import InvalidCacheTTLException
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO


class TestCacheTTLVO:
    @pytest.mark.parametrize("seconds", [0, 1, 60, 3600, 2592000])
    def test_should_create_cache_ttl_when_seconds_is_valid(self, seconds: int) -> None:
        cache_ttl = CacheTTLVO(seconds=seconds)

        assert cache_ttl.seconds == seconds
        assert cache_ttl.value() == seconds

    def test_should_raise_exception_when_seconds_is_none(self) -> None:
        with pytest.raises(InvalidCacheTTLException):
            CacheTTLVO(seconds=None)  # type: ignore[arg-type]

    def test_should_raise_exception_when_seconds_is_not_an_integer(self) -> None:
        with pytest.raises(InvalidCacheTTLException):
            CacheTTLVO(seconds=12.5)  # type: ignore[arg-type]

    def test_should_raise_exception_when_seconds_is_negative(self) -> None:
        with pytest.raises(InvalidCacheTTLException):
            CacheTTLVO(seconds=-1)

    def test_should_raise_exception_when_seconds_exceeds_thirty_days(self) -> None:
        with pytest.raises(InvalidCacheTTLException):
            CacheTTLVO(seconds=2592001)

    def test_should_be_immutable_when_created(self) -> None:
        cache_ttl = CacheTTLVO(seconds=60)

        with pytest.raises(FrozenInstanceError):
            cache_ttl.seconds = 120  # type: ignore[misc]

    def test_should_be_equal_when_seconds_have_same_value(self) -> None:
        first = CacheTTLVO(seconds=60)
        second = CacheTTLVO(seconds=60)

        assert first == second

    def test_should_not_be_equal_when_seconds_have_different_value(self) -> None:
        first = CacheTTLVO(seconds=60)
        second = CacheTTLVO(seconds=120)

        assert first != second
