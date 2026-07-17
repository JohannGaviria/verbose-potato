import pytest

from src.shared.domain.value_objects.cache_value_vo import CacheValueVO
from tests.unit.conftest import DummyCacheValueVO


class TestCacheValueVO:
    def test_should_raise_exception_when_instantiated_directly(self) -> None:
        with pytest.raises(TypeError):
            CacheValueVO()  # type: ignore[abstract]

    def test_should_create_concrete_subclass_when_to_dict_is_implemented(self) -> None:
        value = DummyCacheValueVO(payload="hello")

        assert value.payload == "hello"

    def test_should_return_dict_when_to_dict_is_called(self) -> None:
        value = DummyCacheValueVO(payload="hello")

        assert value.to_dict() == {"payload": "hello"}

    def test_should_be_equal_when_subclasses_have_same_value(self) -> None:
        first = DummyCacheValueVO(payload="hello")
        second = DummyCacheValueVO(payload="hello")

        assert first == second

    def test_should_not_be_equal_when_subclasses_have_different_value(self) -> None:
        first = DummyCacheValueVO(payload="hello")
        second = DummyCacheValueVO(payload="world")

        assert first != second

    def test_should_return_none_when_abstract_to_dict_body_is_invoked_directly(
        self,
    ) -> None:
        # CacheValueVO.to_dict is abstract but still has a concrete (empty)
        # body. Calling it unbound covers that body, which no subclass call
        # exercises since every subclass overrides it.
        value = DummyCacheValueVO(payload="hello")

        assert CacheValueVO.to_dict(value) is None
