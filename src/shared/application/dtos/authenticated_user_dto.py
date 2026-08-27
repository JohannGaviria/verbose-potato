"""This module contains the dto for the authenticated user command."""

from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.enums.user_role_enum import UserRoleEnum


@dataclass(frozen=True, slots=True)
class AuthenticatedUserCommandDto:
    """Data Transfer Object for authenticated user command.

    Attributes:
        id (UUID): The user's ID.
        role (UserRoleEnum): The user's role.
    """

    id: UUID
    role: UserRoleEnum
