"""This module contains the user entity class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.enums.user_role_enum import UserRoleEnum


@dataclass(frozen=True, slots=True)
class UserEntity(BaseEntity):
    """Entity representing a user in the system.

    Attributes:
        id (UUID): The unique identifier of the user.
        name (NameVO): The user's name.
        email (EmailVO): The user's email.
        password (PasswordHashVO): The user's password.
        role (UserRoleEnum): The user's role.
        created_at (datetime): The date and time the user was created.
        updated_at (datetime): The date and time the user was last updated.
    """

    name: NameVO
    email: EmailVO
    password: PasswordHashVO
    role: UserRoleEnum

    @classmethod
    def create(
        cls,
        name: NameVO,
        email: EmailVO,
        password: PasswordHashVO,
        role: UserRoleEnum,
    ) -> "UserEntity":
        """Factory method to create a new user entity.

        Args:
            name (NameVO): The user's name.
            email (EmailVO): The user's email.
            password (PasswordHashVO): The user's password.
            role (UserRoleEnum): The user's role.

        Returns:
            UserEntity: The created user entity.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            name=name,
            email=email,
            password=password,
            role=role,
            created_at=now,
            updated_at=now,
        )
