from collections.abc import Callable

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.exceptions.user_exception import UserRepositoryException
from src.modules.auth.infrastructure.persistence.models.user_model import UserModel
from src.modules.auth.infrastructure.persistence.repositories.sqlalchemy_user_repository_adapter import (
    SQLAlchemyUserRepositoryAdapter,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum

UserEntityFactory = Callable[..., UserEntity]

pytestmark = pytest.mark.db


class TestSQLAlchemyUserRepositoryAdapter:
    class TestExistsLibrarian:
        async def test_should_return_false_when_no_user_exists(
            self,
            user_repository: SQLAlchemyUserRepositoryAdapter,
        ) -> None:
            assert await user_repository.exists_librarian() is False

        async def test_should_return_false_when_only_members_exist(
            self,
            user_repository: SQLAlchemyUserRepositoryAdapter,
            make_user_entity: UserEntityFactory,
        ) -> None:
            await user_repository.save(make_user_entity(role=UserRoleEnum.MEMBER))
            await user_repository.save(make_user_entity(role=UserRoleEnum.MEMBER))

            assert await user_repository.exists_librarian() is False

        async def test_should_return_true_when_a_librarian_exists(
            self,
            user_repository: SQLAlchemyUserRepositoryAdapter,
            make_user_entity: UserEntityFactory,
        ) -> None:
            await user_repository.save(make_user_entity(role=UserRoleEnum.LIBRARIAN))

            assert await user_repository.exists_librarian() is True

        async def test_should_return_true_when_a_librarian_exists_among_members(
            self,
            user_repository: SQLAlchemyUserRepositoryAdapter,
            make_user_entity: UserEntityFactory,
        ) -> None:
            await user_repository.save(make_user_entity(role=UserRoleEnum.MEMBER))
            await user_repository.save(make_user_entity(role=UserRoleEnum.LIBRARIAN))

            assert await user_repository.exists_librarian() is True

        async def test_should_raise_user_repository_exception_when_a_database_error_occurs(
            self,
            user_repository: SQLAlchemyUserRepositoryAdapter,
            db_session: AsyncSession,
        ) -> None:
            # Drop the table out from under the adapter to force a real,
            # unmocked SQLAlchemyError (rather than IntegrityError) so the
            # generic error-handling branch is exercised end to end.
            await db_session.execute(text("DROP TABLE users"))

            with pytest.raises(UserRepositoryException):
                await user_repository.exists_librarian()

    class TestSave:
        async def test_should_persist_user_when_entity_is_valid(
            self,
            user_repository: SQLAlchemyUserRepositoryAdapter,
            db_session: AsyncSession,
            make_user_entity: UserEntityFactory,
        ) -> None:
            entity = make_user_entity()

            await user_repository.save(entity)

            persisted = await db_session.get(UserModel, entity.id)
            assert persisted is not None
            assert persisted.name == entity.name.value
            assert persisted.email == entity.email.value
            assert persisted.password == entity.password.password_hash
            assert persisted.role == entity.role.value

        async def test_should_return_saved_entity_with_matching_attributes(
            self,
            user_repository: SQLAlchemyUserRepositoryAdapter,
            make_user_entity: UserEntityFactory,
        ) -> None:
            entity = make_user_entity(role=UserRoleEnum.LIBRARIAN)

            saved = await user_repository.save(entity)

            assert saved == entity
            assert saved.id == entity.id
            assert saved.name == entity.name
            assert saved.email == entity.email
            assert saved.password == entity.password
            assert saved.role == entity.role
            assert saved.created_at == entity.created_at
            assert saved.updated_at == entity.updated_at

        async def test_should_raise_user_repository_exception_when_email_already_exists(
            self,
            user_repository: SQLAlchemyUserRepositoryAdapter,
            make_user_entity: UserEntityFactory,
        ) -> None:
            duplicate_email = "duplicate.user@example.com"
            await user_repository.save(make_user_entity(email=duplicate_email))

            with pytest.raises(UserRepositoryException):
                await user_repository.save(make_user_entity(email=duplicate_email))

        async def test_should_raise_user_repository_exception_when_a_database_error_occurs(
            self,
            user_repository: SQLAlchemyUserRepositoryAdapter,
            db_session: AsyncSession,
            make_user_entity: UserEntityFactory,
        ) -> None:
            await db_session.execute(text("DROP TABLE users"))

            with pytest.raises(UserRepositoryException):
                await user_repository.save(make_user_entity())
