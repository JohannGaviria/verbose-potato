"""This module contains the SQLAlchemy user repository adapter class."""

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.exceptions.user_exception import UserRepositoryException
from src.modules.auth.domain.ports.repositories.user_repository_port import (
    UserRepositoryPort,
)
from src.modules.auth.infrastructure.persistence.mappers.user_persistence_mapper import (
    UserPersistenceMapper,
)
from src.modules.auth.infrastructure.persistence.models.user_model import UserModel
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyUserRepositoryAdapter(UserRepositoryPort):
    """Adapter used to interact with the SQLAlchemy user repository."""

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyUserRepositoryAdapter.

        Args:
            session (AsyncSession): Database session used to interact with the database.
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
        """
        self._session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def exists_librarian(self) -> bool:
        """Check if exists a librarian.

        Returns:
            bool: True if exists a librarian, False otherwise.

        Raises:
            UserRepositoryException: If an error occurs while checking if a librarian exists.
        """
        try:
            stmt = select(exists().where(UserModel.role == UserRoleEnum.LIBRARIAN))
            result = await self._session.execute(stmt)
            return result.scalar_one()

        except SQLAlchemyError as exc:
            self._logger.error(
                "Error while checking if a librarian exists.",
                error=str(exc),
            )
            raise UserRepositoryException(
                "Error while checking if a librarian exists."
            ) from exc

    async def save(self, entity: UserEntity) -> UserEntity:
        """Persists a UserEntity within the current transaction and returns it.

        Args:
            entity (UserEntity): The user entity to be saved.

        Returns:
            UserEntity: The saved user entity.

        Raises:
            UserRepositoryException: If an error occurs while saving the user.
        """
        try:
            model = UserPersistenceMapper.to_model(entity)
            self._session.add(model)
            await self._session.flush()
            await self._session.refresh(model)
            return UserPersistenceMapper.to_entity(model)

        except IntegrityError as exc:
            self._logger.error("Integrity error while saving user", exc_info=str(exc))
            raise UserRepositoryException(
                "User already exists or violates constraints"
            ) from exc

        except SQLAlchemyError as exc:
            self._logger.error("Database error while saving user", exc_info=str(exc))
            raise UserRepositoryException(
                "Database error during user creation."
            ) from exc
