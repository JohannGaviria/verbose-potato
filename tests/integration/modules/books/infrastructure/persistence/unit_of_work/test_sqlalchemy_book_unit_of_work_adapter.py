from collections.abc import Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.infrastructure.persistence.models.book_model import BookModel
from src.modules.books.infrastructure.persistence.repositories.sqlalchemy_book_repository_adapter import (
    SQLAlchemyBookRepositoryAdapter,
)
from src.modules.books.infrastructure.persistence.unit_of_work.sqlalchemy_book_unit_of_work_adapter import (
    SQLAlchemyBookUnitOfWorkAdapter,
)

BookEntityFactory = Callable[..., BookEntity]

pytestmark = pytest.mark.db


class TestSQLAlchemyBookUnitOfWorkAdapter:
    async def test_should_expose_books_repository_when_context_is_entered(
        self,
        book_unit_of_work: SQLAlchemyBookUnitOfWorkAdapter,
    ) -> None:
        async with book_unit_of_work as uow:
            assert isinstance(uow.books, SQLAlchemyBookRepositoryAdapter)

    async def test_should_persist_changes_when_commit_is_called(
        self,
        book_unit_of_work: SQLAlchemyBookUnitOfWorkAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        make_book_entity: BookEntityFactory,
    ) -> None:
        entity = make_book_entity()

        async with book_unit_of_work as uow:
            await uow.books.save(entity)
            await uow.commit()

        async with session_factory() as verification_session:
            persisted = await verification_session.get(BookModel, entity.id)
            assert persisted is not None
            assert persisted.isbn == entity.isbn.value

    async def test_should_not_persist_changes_when_commit_is_not_called(
        self,
        book_unit_of_work: SQLAlchemyBookUnitOfWorkAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        make_book_entity: BookEntityFactory,
    ) -> None:
        entity = make_book_entity()

        async with book_unit_of_work as uow:
            await uow.books.save(entity)

        async with session_factory() as verification_session:
            persisted = await verification_session.get(BookModel, entity.id)
            assert persisted is None

    async def test_should_rollback_changes_when_exception_escapes_the_block(
        self,
        book_unit_of_work: SQLAlchemyBookUnitOfWorkAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        make_book_entity: BookEntityFactory,
    ) -> None:
        entity = make_book_entity()

        with pytest.raises(RuntimeError):
            async with book_unit_of_work as uow:
                await uow.books.save(entity)
                raise RuntimeError("simulated use case failure")

        async with session_factory() as verification_session:
            persisted = await verification_session.get(BookModel, entity.id)
            assert persisted is None

    async def test_should_discard_changes_when_rollback_is_called_explicitly(
        self,
        book_unit_of_work: SQLAlchemyBookUnitOfWorkAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        make_book_entity: BookEntityFactory,
    ) -> None:
        entity = make_book_entity()

        async with book_unit_of_work as uow:
            await uow.books.save(entity)
            await uow.rollback()

        async with session_factory() as verification_session:
            persisted = await verification_session.get(BookModel, entity.id)
            assert persisted is None

    async def test_should_provide_a_fresh_session_on_each_use(
        self,
        book_unit_of_work: SQLAlchemyBookUnitOfWorkAdapter,
    ) -> None:
        async with book_unit_of_work as first_use:
            first_session = first_use._session

        async with book_unit_of_work as second_use:
            second_session = second_use._session

        assert first_session is not second_session

    async def test_should_raise_runtime_error_when_commit_called_outside_context(
        self,
        book_unit_of_work: SQLAlchemyBookUnitOfWorkAdapter,
    ) -> None:
        with pytest.raises(RuntimeError):
            await book_unit_of_work.commit()

    async def test_should_raise_runtime_error_when_rollback_called_outside_context(
        self,
        book_unit_of_work: SQLAlchemyBookUnitOfWorkAdapter,
    ) -> None:
        with pytest.raises(RuntimeError):
            await book_unit_of_work.rollback()
