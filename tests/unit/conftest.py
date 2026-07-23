from dataclasses import dataclass
from unittest.mock import AsyncMock, Mock

import pytest

from src.shared.domain.value_objects.cache_value_vo import CacheValueVO


@dataclass(frozen=True, slots=True)
class DummyCacheValueVO(CacheValueVO):
    """Minimal concrete CacheValueVO used to exercise CacheEntryVO."""

    payload: str

    def to_dict(self) -> dict:
        return {"payload": self.payload}


@pytest.fixture
def logger_factory_outbound_mock() -> Mock:
    return Mock()


@pytest.fixture
def password_hash_outbound_mock() -> Mock:
    return Mock()


@pytest.fixture
def user_repository_mock() -> AsyncMock:
    return AsyncMock()
