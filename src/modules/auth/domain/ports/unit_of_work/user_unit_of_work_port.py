"""This module contains the user unit of work port class."""

from abc import abstractmethod

from src.modules.auth.domain.ports.repositories.user_repository_port import (
    UserRepositoryPort,
)
from src.shared.domain.ports.unit_of_work.unit_of_work_port import UnitOfWorkPort


class UserUnitOfWorkPort(UnitOfWorkPort):
    """Unit of work port for user operations.

    Attributes:
        users (UserRepositoryPort): Repository used to interact with the user entity.
    """

    users: UserRepositoryPort

    @abstractmethod
    async def __aenter__(self) -> "UserUnitOfWorkPort":
        """Enter the unit of work context.

        Returns:
            UserUnitOfWorkPort: The unit of work context.
        """
        pass
