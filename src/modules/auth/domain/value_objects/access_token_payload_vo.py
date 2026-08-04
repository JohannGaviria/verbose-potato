"""This module contains the access token payload value object."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from src.modules.auth.domain.exceptions.authentication_exception import (
    InvalidAccessTokenPayloadException,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class AccessTokenPayloadVO(BaseValueObject):
    """Value object for access token payload.

    Attributes:
        jti (UUID): The unique identifier for the token.
        sub (UUID): The unique identifier for the user.
        role (UserRoleEnum): The user's role.
        exp (datetime): The expiration time for the token.
    """

    jti: UUID
    sub: UUID
    role: UserRoleEnum
    exp: datetime

    def _validate(self) -> None:
        """Validates the access token payload value object.

        The rules for validating the access token payload value object are:
        - jti cannot be None.
        - sub cannot be None.
        - role cannot be None.
        - exp cannot be None.
        - jti must be a UUID.
        - sub must be a UUID.
        - role must be a UserRoleEnum.
        - exp must be a datetime.
        - exp must be timezone-aware.
        - exp must be in the future.

        Raises:
            InvalidAccessTokenPayloadException: If the access token payload is invalid.
        """
        if self.jti is None:
            raise InvalidAccessTokenPayloadException("jti cannot be None.")
        if self.sub is None:
            raise InvalidAccessTokenPayloadException("sub cannot be None.")
        if self.role is None:
            raise InvalidAccessTokenPayloadException("role cannot be None.")
        if self.exp is None:
            raise InvalidAccessTokenPayloadException("exp cannot be None.")
        if not isinstance(self.jti, UUID):
            raise InvalidAccessTokenPayloadException("jti must be a UUID.")
        if not isinstance(self.sub, UUID):
            raise InvalidAccessTokenPayloadException("sub must be a UUID.")
        if not isinstance(self.role, UserRoleEnum):
            raise InvalidAccessTokenPayloadException("role must be a UserRoleEnum.")
        if not isinstance(self.exp, datetime):
            raise InvalidAccessTokenPayloadException("exp must be a datetime.")
        if self.exp.tzinfo is None:
            raise InvalidAccessTokenPayloadException("exp must be timezone-aware.")
        if self.exp <= datetime.now(UTC):
            raise InvalidAccessTokenPayloadException("exp must be a future datetime.")

    def to_dict(self) -> dict:
        """Returns the access token payload as a dictionary.

        Returns:
            dict: The access token payload as a dictionary.
        """
        return {
            "jti": self.jti,
            "sub": self.sub,
            "role": self.role,
            "exp": self.exp,
        }
