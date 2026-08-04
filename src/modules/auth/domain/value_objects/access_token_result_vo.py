"""This module contains the access token result value object."""

from dataclasses import dataclass

from src.modules.auth.domain.exceptions.authentication_exception import (
    InvalidAccessTokenResultException,
)
from src.modules.auth.domain.value_objects.access_token_vo import AccessTokenVO
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class AccessTokenResultVO(BaseValueObject):
    """Value object for access token result.

    Attributes:
        access_token (AccessTokenVO): The access token.
        token_type (str): The type of token.
        expires_in (int): The number of seconds until the token expires.
    """

    access_token: AccessTokenVO
    token_type: str
    expires_in: int

    def _validate(self) -> None:
        """Validates the access token result value object.

        The rules for validating the access token result value object are:
        - Access token cannot be None.
        - Token type cannot be None.
        - Expires in cannot be None.
        - Access token must be a string.
        - Token type must be a string.
        - Expires in must be an integer.
        - Expires in must be greater than 0.

        Raises:
            InvalidAccessTokenResultException: If the access token result is invalid.
        """
        if self.access_token is None:
            raise InvalidAccessTokenResultException("Access token cannot be None.")
        if self.token_type is None:
            raise InvalidAccessTokenResultException("Token type cannot be None.")
        if self.expires_in is None:
            raise InvalidAccessTokenResultException("Expires in cannot be None.")
        if not isinstance(self.access_token, AccessTokenVO):
            raise InvalidAccessTokenResultException(
                "Access token must be an AccessTokenVO."
            )
        if not isinstance(self.token_type, str):
            raise InvalidAccessTokenResultException("Token type must be a string.")
        if not isinstance(self.expires_in, int):
            raise InvalidAccessTokenResultException("Expires in must be an integer.")
        if self.expires_in <= 0:
            raise InvalidAccessTokenResultException(
                "Expires in must be greater than 0."
            )
