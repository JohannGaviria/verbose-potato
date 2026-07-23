"""This module contains the plain password vo class."""

from dataclasses import dataclass

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidPlainPasswordException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class PlainPasswordVO(BaseValueObject):
    """Value object representing a plain password.

    Attributes:
        plain_password (str): The plain password.
    """

    plain_password: str

    def _validate(self) -> None:
        """Validates the rules for the plain password value object.

        The rules for the plain password value object are:
        - The plain password cannot be None.
        - The plain password must be a string.
        - The plain password cannot be empty.
        - The plain password cannot be less than 8 characters.
        - The plain password cannot be longer than 16 characters.
        - The plain password must contain at least a lowercase letter.
        - The plain password must contain at least an uppercase letter.
        - The plain password must contain at least a digit.
        - The plain password must contain at least a special character.

        Raises:
            InvalidPlainPasswordException: If the plain password is not valid.
        """
        SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?/\\"

        if self.plain_password is None:
            raise InvalidPlainPasswordException("Password cannot be None.")
        if not isinstance(self.plain_password, str):
            raise InvalidPlainPasswordException("Password must be a string.")
        if not self.plain_password.strip():
            raise InvalidPlainPasswordException("Password cannot be empty.")
        if len(self.plain_password) < 8:
            raise InvalidPlainPasswordException(
                "Password must be at least 8 characters."
            )
        if len(self.plain_password) > 16:
            raise InvalidPlainPasswordException(
                "Password must be at most 16 characters."
            )
        if not any(c.islower() for c in self.plain_password):
            raise InvalidPlainPasswordException(
                "Password must contain a lowercase letter."
            )
        if not any(c.isupper() for c in self.plain_password):
            raise InvalidPlainPasswordException(
                "Password must contain an uppercase letter."
            )
        if not any(c.isdigit() for c in self.plain_password):
            raise InvalidPlainPasswordException("Password must contain a digit.")
        if not any(c in SPECIAL_CHARS for c in self.plain_password):
            raise InvalidPlainPasswordException(
                "Password must contain a special character."
            )

    @property
    def value(self) -> str:
        """Returns the plain password as a string.

        Returns:
            str: the plain password.
        """
        return self.plain_password
