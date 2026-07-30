"""This module contains the Argon2 password hash outbound adapter class."""

from argon2 import PasswordHasher

from src.modules.auth.domain.ports.outbound.password_hash_outbound_port import (
    PasswordHashOutboundPort,
)
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO


class Argon2PasswordHashOutboundAdapter(PasswordHashOutboundPort):
    """Adapter used to hash passwords using the Argon2 algorithm."""

    def __init__(
        self, time_cost: int = 3, memory_cost: int = 65536, parallelism: int = 4
    ) -> None:
        """Initialize the Argon2 password hasher with specific parameters.

        Args:
            time_cost (int): The number of iterations (default is 3).
            memory_cost (int): The amount of memory to use (default is 65536 KB).
            parallelism (int): The number of parallel threads to use (default is 4).
        """
        self._hasher = PasswordHasher(time_cost, memory_cost, parallelism)

    def hash(self, plain_password: PlainPasswordVO) -> PasswordHashVO:
        """Hashes a plain-text password using the Argon2 algorithm.

        Args:
            plain_password (PlainPasswordVO): The plain-text password to be hashed.

        Returns:
            PasswordHashVO: The hashed password.
        """
        hashed = self._hasher.hash(plain_password.value)
        return PasswordHashVO(hashed)
