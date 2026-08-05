"""This module contains the access token claims value object."""

from dataclasses import dataclass
from uuid import UUID

from src.modules.auth.domain.exceptions.authentication_exception import (
    InvalidAccessTokenClaimsException,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class AccessTokenClaimsVO(BaseValueObject):
    """Value object for access token claims.

    Attributes:
        sub (UUID): The unique identifier for the user.
        role (UserRoleEnum): The user's role.
    """

    sub: UUID
    role: UserRoleEnum

    def _validate(self) -> None:
        """Validates the access token claims value object.

        The rules for validating the access token claims value object are:
        - sub cannot be None.
        - role cannot be None.
        - sub must be a UUID.
        - role must be a UserRoleEnum.

        Raises:
            InvalidAccessTokenClaimsException: If the access token claims are invalid.
        """
        if self.sub is None:
            raise InvalidAccessTokenClaimsException("sub cannot be None.")
        if self.role is None:
            raise InvalidAccessTokenClaimsException("role cannot be None.")
        if not isinstance(self.sub, UUID):
            raise InvalidAccessTokenClaimsException("sub must be a UUID.")
        if not isinstance(self.role, UserRoleEnum):
            raise InvalidAccessTokenClaimsException("role must be a UserRoleEnum.")

    @classmethod
    def create(cls, sub: UUID, role: UserRoleEnum) -> "AccessTokenClaimsVO":
        """Factory method to create an instance of AccessTokenClaimsVO.

        Args:
            sub (UUID): The unique identifier for the user.
            role (UserRoleEnum): The user's role.

        Returns:
            AccessTokenClaimsVO: The created instance.
        """
        return cls(sub=sub, role=role)
