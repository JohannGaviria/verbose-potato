from dataclasses import FrozenInstanceError
from typing import Any

import pytest
from faker import Faker

from src.modules.auth.domain.exceptions.authentication_exception import (
    InvalidAccessTokenException,
)
from src.modules.auth.domain.value_objects.access_token_vo import AccessTokenVO


class TestAccessTokenVO:
    def test_should_return_token_as_string_when_valid_token_is_provided(
        self, faker: Faker
    ) -> None:
        token = faker.sha256()
        access_token_vo = AccessTokenVO(token)

        assert access_token_vo.value == token

    def test_should_raise_exception_when_token_is_none(self) -> None:
        with pytest.raises(InvalidAccessTokenException):
            AccessTokenVO(None)  # type: ignore[arg-type]

    def test_should_raise_exception_when_token_is_empty(self) -> None:
        with pytest.raises(InvalidAccessTokenException):
            AccessTokenVO("")

    @pytest.mark.parametrize("token", [123, True, False, [], {}])
    def test_should_raise_exception_when_token_is_not_a_string(
        self, token: Any
    ) -> None:
        with pytest.raises(InvalidAccessTokenException):
            AccessTokenVO(token)

    @pytest.mark.parametrize(
        "token",
        [
            " ",
            "   ",
            "\t",
            "\n",
            "\r\n",
        ],
    )
    def test_should_raise_exception_when_token_is_whitespace_only(
        self, token: str
    ) -> None:
        with pytest.raises(InvalidAccessTokenException):
            AccessTokenVO(token)

    def test_should_raise_exception_when_attempting_to_modify_token(
        self, faker: Faker
    ) -> None:
        access_token_vo = AccessTokenVO(faker.sha256())

        with pytest.raises(FrozenInstanceError):
            access_token_vo.token = faker.sha256()  # type: ignore[misc]
