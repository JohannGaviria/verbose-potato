from collections.abc import Callable

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.config import settings
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)
from src.modules.auth.infrastructure.persistence.repositories.sqlalchemy_user_repository_adapter import (
    SQLAlchemyUserRepositoryAdapter,
)
from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)

UserEntityFactory = Callable[..., UserEntity]


@pytest.fixture
def make_user_entity(faker: Faker) -> UserEntityFactory:
    """Factory for building a valid ``UserEntity`` with sensible fake defaults.

    Any attribute can be overridden, e.g. ``make_user_entity(role=UserRoleEnum.LIBRARIAN)``.
    """

    def _make(
        *,
        name: str | None = None,
        email: str | None = None,
        password_hash: str | None = None,
        role: UserRoleEnum = UserRoleEnum.MEMBER,
    ) -> UserEntity:
        return UserEntity.create(
            name=NameVO(name or faker.name()),
            email=EmailVO(email or faker.unique.email()),
            password=PasswordHashVO(password_hash or faker.text(max_nb_chars=60)),
            role=role,
        )

    return _make


@pytest.fixture
def user_repository(
    db_session: AsyncSession,
    logger_factory_outbound: LoggerFactoryOutboundPort,
) -> SQLAlchemyUserRepositoryAdapter:
    return SQLAlchemyUserRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture
def user_unit_of_work(
    session_factory: async_sessionmaker[AsyncSession],
    logger_factory_outbound: LoggerFactoryOutboundPort,
) -> SQLAlchemyUserUnitOfWorkAdapter:
    return SQLAlchemyUserUnitOfWorkAdapter(
        session_factory=session_factory,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture
def password_hash_outbound() -> Argon2PasswordHashOutboundAdapter:
    return Argon2PasswordHashOutboundAdapter(
        time_cost=settings.ARGON2_TIME_COST,
        memory_cost=settings.ARGON2_MEMORY_COST,
        parallelism=settings.ARGON2_PARALLELISM,
    )
