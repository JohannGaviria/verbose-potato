"""This module contains the domain service for authorization."""

from uuid import UUID

from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.authentication_authorization_exception import (
    InsufficientPermissionsException,
)


class AuthorizationService:
    """Domain service for authorization checks.

    Centralizes authorization rules that are shared across
    multiple use cases.

    Usage::

        authorization_service = AuthorizationService()

        authorization_service.assert_role(
            user_role=user_role,
            required_role=UserRoleEnum.LIBRARIAN,
        )

        authorization_service.assert_ownership(
            resource_owner_id=resource.user_id,
            user_id=user_id,
        )
    """

    def assert_role(
        self,
        user_role: UserRoleEnum,
        required_role: UserRoleEnum,
    ) -> None:
        """Asserts that the user has the required role.

        Args:
            user_role (UserRoleEnum): The user's current role.
            required_role (UserRoleEnum): The role required to perform the action.

        Raises:
            InsufficientPermissionsException: If the user's role does not match the required role.
        """
        if user_role != required_role:
            raise InsufficientPermissionsException(
                "The user does not have the required role to perform this action."
            )

    def assert_ownership(
        self,
        resource_owner_id: UUID,
        user_id: UUID,
    ) -> None:
        """Asserts that the user owns the resource.

        Args:
            resource_owner_id (UUID): The ID of the resource owner.
            user_id (UUID): The ID of the user attempting to access the resource.

        Raises:
            InsufficientPermissionsException: If the user is not the owner of the resource.
        """
        if resource_owner_id != user_id:
            raise InsufficientPermissionsException(
                "The user does not have permission to access this resource."
            )
