import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.application.dtos.create_first_librarian_dto import (
    CreateFirstLibrarianCommandDto,
)
from src.modules.auth.application.use_cases.create_first_librarian_use_case import (
    CreateFirstLibrarianUseCase,
)
from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)
from src.modules.auth.infrastructure.persistence.models.user_model import UserModel
from src.modules.auth.infrastructure.persistence.repositories.sqlalchemy_user_repository_adapter import (
    SQLAlchemyUserRepositoryAdapter,
)
from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.modules.auth.presentation.system.runners.create_first_librarian_runner import (
    CreateFirstLibrarianRunner,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)

pytestmark = pytest.mark.db


class TestCreateFirstLibrarianRunner:
    async def test_should_create_first_librarian_when_runner_is_executed(
        self,
        user_unit_of_work: SQLAlchemyUserUnitOfWorkAdapter,
        password_hash_outbound: Argon2PasswordHashOutboundAdapter,
        logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
        faker: Faker,
        db_session: AsyncSession,
    ) -> None:
        use_case = CreateFirstLibrarianUseCase(
            logger_factory_outbound=logger_factory_outbound,
            user_unit_of_work=user_unit_of_work,
            password_hash_outbound=password_hash_outbound,
        )

        name = faker.name()
        email = faker.email()

        runner = CreateFirstLibrarianRunner(
            logger_factory_outbound=logger_factory_outbound,
            create_first_librarian_use_case=use_case,
            data=CreateFirstLibrarianCommandDto(
                name=name,
                email=email,
                password=faker.password(),
            ),
        )

        await runner.run()

        result = await db_session.execute(
            select(UserModel).where(UserModel.email == email)
        )

        user = result.scalar_one()

        assert user is not None
        assert user.name == name
        assert user.email == email
        assert user.role == UserRoleEnum.LIBRARIAN.value

    async def test_should_not_create_second_librarian_when_runner_is_executed_twice(
        self,
        user_repository: SQLAlchemyUserRepositoryAdapter,
        user_unit_of_work: SQLAlchemyUserUnitOfWorkAdapter,
        password_hash_outbound: Argon2PasswordHashOutboundAdapter,
        logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
        faker: Faker,
        db_session: AsyncSession,
    ) -> None:
        use_case = CreateFirstLibrarianUseCase(
            logger_factory_outbound=logger_factory_outbound,
            user_unit_of_work=user_unit_of_work,
            password_hash_outbound=password_hash_outbound,
        )

        name = faker.name()
        email = faker.email()

        runner = CreateFirstLibrarianRunner(
            logger_factory_outbound=logger_factory_outbound,
            create_first_librarian_use_case=use_case,
            data=CreateFirstLibrarianCommandDto(
                name=name,
                email=email,
                password=faker.password(),
            ),
        )

        await runner.run()

        await runner.run()

        assert await user_repository.exists_librarian() is True

        result = await db_session.execute(
            select(UserModel).where(UserModel.email == email)
        )

        user = result.scalar_one()

        assert user is not None
        assert user.role == UserRoleEnum.LIBRARIAN.value
