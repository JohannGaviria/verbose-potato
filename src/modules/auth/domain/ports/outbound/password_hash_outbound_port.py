"""This module contains the password hash outbound port class."""

from abc import ABC, abstractmethod

from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO


class PasswordHashOutboundPort(ABC):
    """Outbound port for password hashing."""

    @abstractmethod
    def hash(self, plain_password: PlainPasswordVO) -> PasswordHashVO:
        """Hash a plain password and return the hashed version.

        Args:
            plain_password (PlainPasswordVO): The plain password to be hashed.

        Returns:
            PasswordHashVO: The hashed password.
        """
        pass

    @abstractmethod
    def verify(
        self, plain_password: PlainPasswordVO, hashed_password: PasswordHashVO
    ) -> bool:
        """Verify if a plain password matches a hashed password.

        Args:
            plain_password (PlainPasswordVO): The plain password to be verified.
            hashed_password (PasswordHashVO): The hashed password to be verified.

        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """
        pass
