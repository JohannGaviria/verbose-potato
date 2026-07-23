"""This module contains the email value object class."""

import re
from dataclasses import dataclass

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidEmailException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class EmailVO(BaseValueObject):
    """Value object representing an email address.

    Attributes:
        email (str): The email address.
    """

    email: str

    def _validate(self) -> None:
        """Validates the rules for the email value object.

        The rules for the email value object are:
        - Email cannot be None.
        - Email must be a string.
        - Email cannot be empty.
        - Email cannot be whitespace only.
        - Email cannot contain whitespace characters.
        - Email cannot contain consecutive dots.
        - Email must match a standard email format.
        - Email cannot exceed 255 characters in length.

        Raises:
            InvalidEmailException: If the email address does not meet the validation criteria.
        """
        # This regex pattern is a simplified version that covers most common email formats,
        # but it may not cover all edge cases defined in the RFC 5322 standard.
        EMAIL_PATTERN = (
            r"^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,6}$"
        )

        if self.email is None:
            raise InvalidEmailException("Email cannot be None.", self.email)
        if not isinstance(self.email, str):
            raise InvalidEmailException("Email must be a string.", self.email)
        if not self.email.strip():
            raise InvalidEmailException("Email cannot be whitespace only.", self.email)
        if any(w in self.email for w in (" ", "\t", "\n")):
            raise InvalidEmailException(
                "Email cannot contain whitespace characters.", self.email
            )
        if ".." in self.email:
            raise InvalidEmailException(
                "Email cannot contain consecutive dots.", self.email
            )
        if not re.match(EMAIL_PATTERN, self.email):
            raise InvalidEmailException("Email format is invalid.", self.email)
        if len(self.email) > 255:
            raise InvalidEmailException(
                "Email cannot exceed 255 characters.", self.email
            )

    @property
    def value(self) -> str:
        """Returns the email as a string.

        Returns:
            str: the email.
        """
        return self.email
