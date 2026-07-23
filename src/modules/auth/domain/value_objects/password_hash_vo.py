"""This module contains the password hash value object class."""

from dataclasses import dataclass

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidPasswordHashException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class PasswordHashVO(BaseValueObject):
    """Value object representing a password hash.

    Attributes:
        password_hash (str): The password hash.
    """

    password_hash: str

    def _validate(self) -> None:
        """Validates the rules for the password hash value object.

        The rules for the password hash value object are:
        - Password hash cannot be None.
        - Password hash must be a string.
        - Password hash cannot be empty.

        Raises:
            InvalidPasswordHashException: If the password hash is invalid.
        """
        if self.password_hash is None:
            raise InvalidPasswordHashException("Password hash cannot be None.")
        if not isinstance(self.password_hash, str):
            raise InvalidPasswordHashException("Password hash must be a string.")
        if not self.password_hash.strip():
            raise InvalidPasswordHashException("Password hash cannot be empty.")
