from dataclasses import FrozenInstanceError

import pytest
from faker import Faker

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidPlainPasswordException,
)
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO


class TestPlainPasswordVO:
    def test_should_return_plain_password_as_string_when_valid_password_is_provided(
        self, faker: Faker
    ) -> None:
        plain_password = faker.password()
        plain_password_vo = PlainPasswordVO(plain_password)

        assert plain_password_vo.value == plain_password

    def test_should_raise_exception_when_plain_password_is_none(self) -> None:
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(None)  # type: ignore[arg-type]

    def test_should_raise_exception_when_plain_password_is_empty(self) -> None:
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO("")

    @pytest.mark.parametrize("password", [123, True, False, None])
    def test_should_raise_exception_when_plain_password_is_not_a_string(
        self, password: object
    ) -> None:
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(password)  # type: ignore[arg-type]

    def test_should_raise_exception_when_plain_password_is_too_short(
        self, faker: Faker
    ) -> None:
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(faker.password(length=7))

    def test_should_raise_exception_when_plain_password_is_too_long(
        self, faker: Faker
    ) -> None:
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(faker.password(length=17))

    def test_should_raise_exception_when_plain_password_is_lowercase_only(
        self, faker: Faker
    ) -> None:
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(faker.password(lower_case=False))

    def test_should_raise_exception_when_plain_password_is_uppercase_only(
        self, faker: Faker
    ) -> None:
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(faker.password(upper_case=False))

    def test_should_raise_exception_when_plain_password_has_no_digits(
        self, faker: Faker
    ) -> None:
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(faker.password(digits=False))

    def test_should_raise_exception_when_plain_password_has_no_special_characters(
        self, faker: Faker
    ) -> None:
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(faker.password(special_chars=False))

    def test_should_raise_exception_when_attempting_to_modify_plain_password(
        self, faker: Faker
    ) -> None:
        plain_password_vo = PlainPasswordVO(faker.password())

        with pytest.raises(FrozenInstanceError):
            plain_password_vo.plain_password = faker.password()  # type: ignore[misc]
