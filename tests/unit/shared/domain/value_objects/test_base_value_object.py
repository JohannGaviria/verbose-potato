from dataclasses import dataclass

import pytest

from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class DummyValueObject(BaseValueObject):
    """Minimal concrete BaseValueObject used to exercise the abstract base."""

    value: str

    def _validate(self) -> None:
        if not self.value:
            raise ValueError("value cannot be empty.")


class TestBaseValueObject:
    def test_should_raise_exception_when_instantiated_directly(self) -> None:
        with pytest.raises(TypeError):
            BaseValueObject()  # type: ignore[abstract]

    def test_should_create_concrete_subclass_when_validation_passes(self) -> None:
        vo = DummyValueObject(value="hello")

        assert vo.value == "hello"

    def test_should_call_validate_when_instantiated(self) -> None:
        with pytest.raises(ValueError):
            DummyValueObject(value="")

    def test_should_return_none_when_abstract_validate_body_is_invoked_directly(
        self,
    ) -> None:
        # BaseValueObject._validate is abstract but still has a concrete
        # (empty) body. Calling it unbound covers that body, which no
        # subclass call exercises since every subclass overrides it.
        vo = DummyValueObject(value="hello")

        assert BaseValueObject._validate(vo) is None
