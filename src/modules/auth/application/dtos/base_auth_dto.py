"""This module contains the base authentication DTO class."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.shared.domain.enums.user_role_enum import UserRoleEnum


@dataclass(frozen=True, slots=True)
class BaseUserDto:
    """Base DTO for user's.

    Attributes:
        name (str): The user's name.
        email (str): The user's email.
    """

    name: str
    email: str


@dataclass(frozen=True, slots=True)
class BaseUserCommandDto(BaseUserDto):
    """Command DTO for user's.

    Attributes:
        name (str): The user's name.
        email (str): The user's email.
        password (str): The user's password.
    """

    password: str


@dataclass(frozen=True, slots=True)
class BaseUserResponseDto(BaseUserDto):
    """Response DTO for user's.

    Attributes:
        name (str): The user's name.
        email (str): The user's email.
        id (UUID): The user's id.
        role (UserRoleEnum): The user's role.
        created_at (datetime): The user's creation date.
        updated_at (datetime): The user's update date.
    """

    id: UUID
    role: UserRoleEnum
    created_at: datetime
    updated_at: datetime
