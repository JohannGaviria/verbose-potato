from dataclasses import FrozenInstanceError
from typing import Any

import pytest
from faker import Faker

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidNameException,
)
from src.modules.auth.domain.value_objects.name_vo import NameVO


class TestNameVO:
    def test_should_return_name_as_string_when_valid_name_is_provided(
        self, faker: Faker
    ) -> None:
        name = faker.name()
        name_vo = NameVO(name)

        assert name_vo.value == name

    def test_should_raise_exception_when_name_is_none(self) -> None:
        with pytest.raises(InvalidNameException):
            NameVO(None)  # type: ignore[arg-type]

    def test_should_raise_exception_when_name_is_empty(self) -> None:
        with pytest.raises(InvalidNameException):
            NameVO("")

    @pytest.mark.parametrize("name", [123, True, False, [], {}])
    def test_should_raise_exception_when_name_is_not_a_string(self, name: Any) -> None:
        with pytest.raises(InvalidNameException):
            NameVO(name)

    @pytest.mark.parametrize(
        "name",
        [
            "",
            " ",
            "   ",
            "\t",
            "\n",
            "\r\n",
        ],
    )
    def test_should_raise_exception_when_name_is_whitespace_only(
        self, name: str
    ) -> None:
        with pytest.raises(InvalidNameException):
            NameVO(name)

    @pytest.mark.parametrize(
        "name",
        [
            "a",
            "ab",
        ],
    )
    def test_should_raise_exception_when_name_is_too_short(self, name: str) -> None:
        with pytest.raises(InvalidNameException):
            NameVO(name)

    def test_should_raise_exception_when_name_exceeds_max_length(
        self, faker: Faker
    ) -> None:
        with pytest.raises(InvalidNameException):
            NameVO(f"{faker.name() * 255}")

    def test_should_raise_exception_when_attempting_to_modify_name(
        self, faker: Faker
    ) -> None:
        name_vo = NameVO(faker.name())

        with pytest.raises(FrozenInstanceError):
            name_vo.name = faker.name()  # type: ignore[misc]
