from dataclasses import dataclass

from src.shared.domain.value_objects.cache_value_vo import CacheValueVO


@dataclass(frozen=True, slots=True)
class DummyCacheValueVO(CacheValueVO):
    """Minimal concrete CacheValueVO used to exercise CacheEntryVO."""

    payload: str

    def to_dict(self) -> dict:
        return {"payload": self.payload}
