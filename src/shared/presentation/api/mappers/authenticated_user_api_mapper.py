"""This module contains the authenticated user Api mapper."""

from uuid import UUID

from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class AuthenticatedUserApiMapper:
    """This class contains methods for mapping between the API and the application layer."""

    @staticmethod
    def to_command(user_id: UUID, role: UserRoleEnum) -> AuthenticatedUserCommandDto:
        """Map a user ID and role to a command DTO.

        Args:
            user_id (UUID): The user ID.
            role (UserRoleEnum): The user role.

        Returns:
            AuthenticatedUserCommandDto: The command DTO.
        """
        return AuthenticatedUserCommandDto(id=user_id, role=role)
