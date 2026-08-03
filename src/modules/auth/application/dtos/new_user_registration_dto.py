"""This module contains the dtos for the new user registration use case class."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.auth.application.dtos.base_auth_dto import (
    BaseUserCommandDto,
    BaseUserResponseDto,
)
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.shared.domain.enums.user_role_enum import UserRoleEnum


@dataclass(frozen=True, slots=True)
class NewUserRegistrationCommandDto(BaseUserCommandDto):
    """Command DTO for new user registration.

    Attributes:
        name (str): The user's name.
        email (str): The user's email.
        password (str): The user's password.
    """

    ...


@dataclass(frozen=True, slots=True)
class NewUserRegistrationResponseDto(BaseUserResponseDto):
    """Response DTO for new user registration.

    Attributes:
        id (UUID): The user's id.
        name (str): The user's name.
        email (str): The user's email.
        role (str): The user's role.
        created_at (datetime): The user's creation date.
        updated_at (datetime): The user's update date.
    """

    id: UUID
    role: UserRoleEnum
    created_at: datetime
    updated_at: datetime

    @classmethod
    def response(cls, user: UserEntity) -> "NewUserRegistrationResponseDto":
        """Factory method to create a new instance of the response DTO.

        Args:
            user (UserEntity): The user entity to be transformed.

        Returns:
            NewUserRegistrationResponseDto: The new instance of the response DTO.
        """
        return cls(
            id=user.id,
            name=user.name.value,
            email=user.email.value,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
