"""This module contains the user repository port class."""

from abc import ABC, abstractmethod

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.email_vo import EmailVO


class UserRepositoryPort(ABC):
    """Repository port for user entities."""

    @abstractmethod
    async def find_by_email(self, email: EmailVO) -> UserEntity | None:
        """Find a user by email.

        Args:
            email (EmailVO): The user's email.

        Returns:
            UserEntity | None: The user entity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def exists_librarian(self) -> bool:
        """Check if exists a librarian.

        Returns:
            bool: True if exists a librarian, False otherwise.
        """
        pass

    @abstractmethod
    async def save(self, entity: UserEntity) -> UserEntity:
        """Save a user entity.

        Args:
            entity (UserEntity): The user entity to be saved.

        Returns:
            UserEntity: The saved user entity.
        """
        pass
