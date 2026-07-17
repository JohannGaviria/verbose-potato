from dataclasses import FrozenInstanceError

import pytest

from src.shared.domain.exceptions.cache_exception import InvalidCacheEntryException
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO
from tests.unit.conftest import DummyCacheValueVO


@pytest.fixture
def valid_key() -> CacheKeyVO:
    return CacheKeyVO(key="cache:user:123")


@pytest.fixture
def valid_ttl() -> CacheTTLVO:
    return CacheTTLVO(seconds=60)


@pytest.fixture
def valid_value() -> DummyCacheValueVO:
    return DummyCacheValueVO(payload="hello")


class TestCacheEntryVO:
    def test_should_create_cache_entry_when_data_is_valid(
        self,
        valid_key: CacheKeyVO,
        valid_ttl: CacheTTLVO,
        valid_value: DummyCacheValueVO,
    ) -> None:
        entry = CacheEntryVO(key=valid_key, ttl=valid_ttl, value=valid_value)

        assert entry.key == valid_key
        assert entry.ttl == valid_ttl
        assert entry.value == valid_value

    def test_should_raise_exception_when_key_is_none(
        self, valid_ttl: CacheTTLVO, valid_value: DummyCacheValueVO
    ) -> None:
        with pytest.raises(InvalidCacheEntryException):
            CacheEntryVO(key=None, ttl=valid_ttl, value=valid_value)  # type: ignore[arg-type]

    def test_should_raise_exception_when_ttl_is_none(
        self, valid_key: CacheKeyVO, valid_value: DummyCacheValueVO
    ) -> None:
        with pytest.raises(InvalidCacheEntryException):
            CacheEntryVO(key=valid_key, ttl=None, value=valid_value)  # type: ignore[arg-type]

    def test_should_raise_exception_when_value_is_none(
        self, valid_key: CacheKeyVO, valid_ttl: CacheTTLVO
    ) -> None:
        with pytest.raises(InvalidCacheEntryException):
            CacheEntryVO(key=valid_key, ttl=valid_ttl, value=None)  # type: ignore[type-var]

    def test_should_raise_exception_when_key_is_not_a_cache_key_vo(
        self, valid_ttl: CacheTTLVO, valid_value: DummyCacheValueVO
    ) -> None:
        with pytest.raises(InvalidCacheEntryException):
            CacheEntryVO(key="cache:user:123", ttl=valid_ttl, value=valid_value)  # type: ignore[arg-type]

    def test_should_raise_exception_when_ttl_is_not_a_cache_ttl_vo(
        self, valid_key: CacheKeyVO, valid_value: DummyCacheValueVO
    ) -> None:
        with pytest.raises(InvalidCacheEntryException):
            CacheEntryVO(key=valid_key, ttl=60, value=valid_value)  # type: ignore[arg-type]

    def test_should_raise_exception_when_value_is_not_a_cache_value_vo(
        self, valid_key: CacheKeyVO, valid_ttl: CacheTTLVO
    ) -> None:
        with pytest.raises(InvalidCacheEntryException):
            CacheEntryVO(key=valid_key, ttl=valid_ttl, value="hello")  # type: ignore[type-var]

    def test_should_be_immutable_when_created(
        self,
        valid_key: CacheKeyVO,
        valid_ttl: CacheTTLVO,
        valid_value: DummyCacheValueVO,
    ) -> None:
        entry = CacheEntryVO(key=valid_key, ttl=valid_ttl, value=valid_value)

        with pytest.raises(FrozenInstanceError):
            entry.key = CacheKeyVO(key="cache:user:456")  # type: ignore[misc]
