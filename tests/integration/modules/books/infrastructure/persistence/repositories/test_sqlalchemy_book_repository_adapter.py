from collections.abc import Callable
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.exceptions.book_exception import BookRepositoryException
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.infrastructure.persistence.models.book_model import BookModel
from src.modules.books.infrastructure.persistence.repositories.sqlalchemy_book_repository_adapter import (
    SQLAlchemyBookRepositoryAdapter,
)

BookEntityFactory = Callable[..., BookEntity]

pytestmark = pytest.mark.db


class TestSQLAlchemyBookRepositoryAdapter:
    class TestExistsByIsbn:
        async def test_should_return_false_when_no_book_exists(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
        ) -> None:
            assert (
                await book_repository.exists_by_isbn(IsbnVO("9780306406157")) is False
            )

        async def test_should_return_true_when_book_exists(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            book = make_book_entity()
            await book_repository.save(book)

            assert await book_repository.exists_by_isbn(book.isbn) is True

        async def test_should_raise_book_repository_exception_when_a_database_error_occurs(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
        ) -> None:
            with patch.object(
                book_repository._session,
                "execute",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(BookRepositoryException):
                    await book_repository.exists_by_isbn(IsbnVO("9780306406157"))

    class TestSave:
        async def test_should_persist_book_when_entity_is_valid(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            db_session: AsyncSession,
            make_book_entity: BookEntityFactory,
        ) -> None:
            entity = make_book_entity()

            await book_repository.save(entity)

            persisted = await db_session.get(BookModel, entity.id)
            assert persisted is not None
            assert persisted.title == entity.title.value
            assert persisted.isbn == entity.isbn.value
            assert persisted.author == entity.author.value
            assert persisted.published_year == entity.published_year.value
            assert persisted.total_copies == entity.total_copies.value
            assert persisted.available_copies == entity.available_copies

        async def test_should_return_saved_entity_with_matching_attributes(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            entity = make_book_entity(total_copies=5)

            saved = await book_repository.save(entity)

            assert saved == entity
            assert saved.id == entity.id
            assert saved.title == entity.title
            assert saved.isbn == entity.isbn
            assert saved.author == entity.author
            assert saved.published_year == entity.published_year
            assert saved.total_copies == entity.total_copies
            assert saved.available_copies == entity.available_copies
            assert saved.created_at == entity.created_at
            assert saved.updated_at == entity.updated_at

        async def test_should_raise_book_repository_exception_when_isbn_already_exists(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            duplicate_isbn = "9780306406157"
            await book_repository.save(make_book_entity(isbn=duplicate_isbn))

            with pytest.raises(BookRepositoryException):
                await book_repository.save(make_book_entity(isbn=duplicate_isbn))

        async def test_should_raise_book_repository_exception_when_a_database_error_occurs_on_add(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            with patch.object(
                book_repository._session,
                "add",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(BookRepositoryException):
                    await book_repository.save(make_book_entity())

        async def test_should_raise_book_repository_exception_when_a_database_error_occurs_on_flush(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            with patch.object(
                book_repository._session,
                "flush",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(BookRepositoryException):
                    await book_repository.save(make_book_entity())

        async def test_should_raise_book_repository_exception_when_a_database_error_occurs_on_refresh(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            with patch.object(
                book_repository._session,
                "refresh",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(BookRepositoryException):
                    await book_repository.save(make_book_entity())
