"""This module contains the access token value object."""

from dataclasses import dataclass

from src.shared.domain.exceptions.authentication_authorization_exception import (
    InvalidAccessTokenException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class AccessTokenVO(BaseValueObject):
    """Value object for access token.

    Attributes:
        token (str): The access token value.
    """

    token: str

    def _validate(self) -> None:
        """Validates the access token value object.

        The rules for validating the access token value object are:
        - Token cannot be None.
        - Token must be a string.
        - Token cannot be empty.

        Raises:
            InvalidAccessTokenException: If the access token is invalid.
        """
        if self.token is None:
            raise InvalidAccessTokenException("Token cannot be None.")
        if not isinstance(self.token, str):
            raise InvalidAccessTokenException("Token must be a string.")
        if not self.token.strip():
            raise InvalidAccessTokenException("Token cannot be empty.")

    @property
    def value(self) -> str:
        """Returns the access token value.

        Returns:
            str: The access token value.
        """
        return self.token
