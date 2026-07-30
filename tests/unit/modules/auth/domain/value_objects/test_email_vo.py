from dataclasses import FrozenInstanceError
from typing import Any

import pytest
from faker import Faker

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidEmailException,
)
from src.modules.auth.domain.value_objects.email_vo import EmailVO


class TestEmailVO:
    def test_should_return_email_as_string_when_valid_email_is_provided(
        self, faker: Faker
    ) -> None:
        email = faker.email()
        email_vo = EmailVO(email)

        assert email_vo.value == email

    def test_should_raise_exception_when_email_is_none(self) -> None:
        with pytest.raises(InvalidEmailException):
            EmailVO(None)  # type: ignore[arg-type]

    def test_should_raise_exception_when_email_is_empty(self) -> None:
        with pytest.raises(InvalidEmailException):
            EmailVO("")

    @pytest.mark.parametrize("email", [123, True, False, [], {}])
    def test_should_raise_exception_when_email_is_not_a_string(
        self, email: Any
    ) -> None:
        with pytest.raises(InvalidEmailException):
            EmailVO(email)

    @pytest.mark.parametrize(
        "email",
        [
            "",
            " ",
            "   ",
            "\t",
            "\n",
            "\r\n",
        ],
    )
    def test_should_raise_exception_when_email_is_whitespace_only(
        self, email: str
    ) -> None:
        with pytest.raises(InvalidEmailException):
            EmailVO(email)

    @pytest.mark.parametrize(
        "email",
        [
            " example@pytest.com",
            "example @pytest.com",
            "example@ pytest.com",
            "example@pytest .com",
            "example@pytest. com",
            "example@pytest.com ",
        ],
    )
    def test_should_raise_exception_when_email_contains_whitespace(
        self, email: str
    ) -> None:
        with pytest.raises(InvalidEmailException):
            EmailVO(email)

    @pytest.mark.parametrize(
        "email",
        [
            "example\t@pytest.com",
            "example\n@pytest.com",
            "example\r@pytest.com",
            "example\r\n@pytest.com",
            "example@\tpytest.com",
            "example@\npytest.com",
        ],
    )
    def test_should_raise_exception_when_email_contains_whitespace_characters(
        self, email: str
    ) -> None:
        with pytest.raises(InvalidEmailException):
            EmailVO(email)

    @pytest.mark.parametrize(
        "email",
        [
            "..example@pytest.com",
            "example..@pytest.com",
            "example@..pytest.com",
            "example@pytest..com",
            "example@pytest.com..co",
            "example@pytest..com..co",
        ],
    )
    def test_should_raise_exception_when_email_contains_consecutive_dots(
        self, email: str
    ) -> None:
        with pytest.raises(InvalidEmailException):
            EmailVO(email)

    @pytest.mark.parametrize(
        "email",
        [
            "example.pytest.com",
            "examplepytest.com",
            "example@pytest",
            "example@.pytest.com",
            "example@-pytest.com",
            "@pytest.com",
        ],
    )
    def test_should_raise_exception_when_email_is_invalid(self, email: str) -> None:
        with pytest.raises(InvalidEmailException):
            EmailVO(email)

    def test_should_raise_exception_when_email_exceeds_max_length(self) -> None:
        domain = "@pytest.com"
        local = "a" * (256 - len(domain))
        email = f"{local}{domain}"

        with pytest.raises(InvalidEmailException):
            EmailVO(email)

    def test_should_raise_exception_when_attempting_to_modify_email(
        self, faker: Faker
    ) -> None:
        email_vo = EmailVO(faker.email())

        with pytest.raises(FrozenInstanceError):
            email_vo.email = faker.email()  # type: ignore[misc]
