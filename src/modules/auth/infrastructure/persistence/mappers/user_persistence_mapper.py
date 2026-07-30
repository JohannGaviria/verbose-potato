"""This module contains the user mapper class."""

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.modules.auth.infrastructure.persistence.models.user_model import UserModel
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class UserPersistenceMapper:
    """Mapper used to map user entities to and from persistence models."""

    @staticmethod
    def to_model(entity: UserEntity) -> UserModel:
        """Maps a user entity to a persistence model.

        Args:
            entity (UserEntity): The user entity to be mapped.

        Returns:
            UserModel: The mapped user model.
        """
        return UserModel(
            id=entity.id,
            name=entity.name.value,
            email=entity.email.value,
            password=entity.password.password_hash,
            role=entity.role.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(model: UserModel) -> UserEntity:
        """Maps a persistence model to a user entity.

        Args:
            model (UserModel): The persistence model to be mapped.

        Returns:
            UserEntity: The mapped user entity.
        """
        return UserEntity(
            id=model.id,
            name=NameVO(model.name),
            email=EmailVO(model.email),
            password=PasswordHashVO(model.password),
            role=UserRoleEnum(model.role),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
