from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidPasswordHashException,
)
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO


class TestPasswordHashVO:
    def test_should_return_password_hash_as_string_when_valid_hash_is_provided(
        self,
    ) -> None:
        password_hash = "password_hash"
        password_hash_vo = PasswordHashVO(password_hash)

        assert password_hash_vo.password_hash == password_hash

    def test_should_raise_exception_when_password_hash_is_none(self) -> None:
        with pytest.raises(InvalidPasswordHashException):
            PasswordHashVO(None)  # type: ignore[arg-type]

    def test_should_raise_exception_when_password_hash_is_empty(self) -> None:
        with pytest.raises(InvalidPasswordHashException):
            PasswordHashVO("")

    @pytest.mark.parametrize("password_hash", [123, True, False, [], {}])
    def test_should_raise_exception_when_password_hash_is_not_a_string(
        self, password_hash: Any
    ) -> None:
        with pytest.raises(InvalidPasswordHashException):
            PasswordHashVO(password_hash)

    def test_should_raise_exception_when_attempting_to_modify_password_hash(
        self,
    ) -> None:
        password_hash = "password_hash"
        password_hash_vo = PasswordHashVO(password_hash)

        with pytest.raises(FrozenInstanceError):
            password_hash_vo.password_hash = password_hash  # type: ignore[misc]
