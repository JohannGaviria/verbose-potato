from collections.abc import Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.infrastructure.persistence.models.user_model import UserModel
from src.modules.auth.infrastructure.persistence.repositories.sqlalchemy_user_repository_adapter import (
    SQLAlchemyUserRepositoryAdapter,
)
from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)

UserEntityFactory = Callable[..., UserEntity]

pytestmark = pytest.mark.db


class TestSQLAlchemyUserUnitOfWorkAdapter:
    async def test_should_expose_users_repository_when_context_is_entered(
        self,
        user_unit_of_work: SQLAlchemyUserUnitOfWorkAdapter,
    ) -> None:
        async with user_unit_of_work as uow:
            assert isinstance(uow.users, SQLAlchemyUserRepositoryAdapter)

    async def test_should_persist_changes_when_commit_is_called(
        self,
        user_unit_of_work: SQLAlchemyUserUnitOfWorkAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        make_user_entity: UserEntityFactory,
    ) -> None:
        entity = make_user_entity()

        async with user_unit_of_work as uow:
            await uow.users.save(entity)
            await uow.commit()

        async with session_factory() as verification_session:
            persisted = await verification_session.get(UserModel, entity.id)
            assert persisted is not None
            assert persisted.email == entity.email.value

    async def test_should_not_persist_changes_when_commit_is_not_called(
        self,
        user_unit_of_work: SQLAlchemyUserUnitOfWorkAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        make_user_entity: UserEntityFactory,
    ) -> None:
        entity = make_user_entity()

        async with user_unit_of_work as uow:
            await uow.users.save(entity)

        async with session_factory() as verification_session:
            persisted = await verification_session.get(UserModel, entity.id)
            assert persisted is None

    async def test_should_rollback_changes_when_exception_escapes_the_block(
        self,
        user_unit_of_work: SQLAlchemyUserUnitOfWorkAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        make_user_entity: UserEntityFactory,
    ) -> None:
        entity = make_user_entity()

        with pytest.raises(RuntimeError):
            async with user_unit_of_work as uow:
                await uow.users.save(entity)
                raise RuntimeError("simulated use case failure")

        async with session_factory() as verification_session:
            persisted = await verification_session.get(UserModel, entity.id)
            assert persisted is None

    async def test_should_discard_changes_when_rollback_is_called_explicitly(
        self,
        user_unit_of_work: SQLAlchemyUserUnitOfWorkAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        make_user_entity: UserEntityFactory,
    ) -> None:
        entity = make_user_entity()

        async with user_unit_of_work as uow:
            await uow.users.save(entity)
            await uow.rollback()

        async with session_factory() as verification_session:
            persisted = await verification_session.get(UserModel, entity.id)
            assert persisted is None

    async def test_should_provide_a_fresh_session_on_each_use(
        self,
        user_unit_of_work: SQLAlchemyUserUnitOfWorkAdapter,
    ) -> None:
        async with user_unit_of_work as first_use:
            first_session = first_use._session

        async with user_unit_of_work as second_use:
            second_session = second_use._session

        assert first_session is not second_session

    async def test_should_raise_runtime_error_when_commit_called_outside_context(
        self,
        user_unit_of_work: SQLAlchemyUserUnitOfWorkAdapter,
    ) -> None:
        with pytest.raises(RuntimeError):
            await user_unit_of_work.commit()

    async def test_should_raise_runtime_error_when_rollback_called_outside_context(
        self,
        user_unit_of_work: SQLAlchemyUserUnitOfWorkAdapter,
    ) -> None:
        with pytest.raises(RuntimeError):
            await user_unit_of_work.rollback()
