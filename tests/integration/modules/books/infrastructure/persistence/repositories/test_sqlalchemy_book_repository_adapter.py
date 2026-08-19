from collections.abc import Callable
from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.exceptions.book_exception import BookRepositoryException
from src.modules.books.domain.value_objects.author_vo import AuthorVO
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.domain.value_objects.published_year_vo import PublishedYearVO
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.modules.books.domain.value_objects.total_copies_vo import TotalCopiesVO
from src.modules.books.infrastructure.persistence.models.book_model import BookModel
from src.modules.books.infrastructure.persistence.repositories.sqlalchemy_book_repository_adapter import (
    SQLAlchemyBookRepositoryAdapter,
)

BookEntityFactory = Callable[..., BookEntity]

pytestmark = pytest.mark.db


class TestSQLAlchemyBookRepositoryAdapter:
    class TestFindById:
        async def test_should_return_none_when_book_does_not_exist(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
        ) -> None:
            assert await book_repository.find_by_id(uuid4()) is None

        async def test_should_return_book_entity_when_book_exists(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            entity = make_book_entity()
            await book_repository.save(entity)

            found = await book_repository.find_by_id(entity.id)

            assert found is not None
            assert found == entity
            assert found.id == entity.id
            assert found.title == entity.title
            assert found.isbn == entity.isbn
            assert found.author == entity.author
            assert found.published_year == entity.published_year
            assert found.total_copies == entity.total_copies
            assert found.available_copies == entity.available_copies

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
                    await book_repository.find_by_id(uuid4())

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

    class TestUpdate:
        async def test_should_persist_changes_when_entity_is_updated(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            db_session: AsyncSession,
            make_book_entity: BookEntityFactory,
        ) -> None:
            entity = make_book_entity(total_copies=5)
            await book_repository.save(entity)

            updated_entity = entity.update(
                title=TitleVO("Updated Title"),
                author=AuthorVO("Updated Author"),
                published_year=PublishedYearVO(2015),
                total_copies=TotalCopiesVO(10),
            )

            await book_repository.update(updated_entity)

            persisted = await db_session.get(BookModel, entity.id)
            assert persisted is not None
            assert persisted.id == entity.id
            assert persisted.isbn == entity.isbn.value
            assert persisted.title == "Updated Title"
            assert persisted.author == "Updated Author"
            assert persisted.published_year == 2015
            assert persisted.total_copies == 10

        async def test_should_return_updated_entity_with_matching_attributes(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            entity = make_book_entity(total_copies=5)
            await book_repository.save(entity)

            updated_entity = entity.update(title=TitleVO("Updated Title"))

            updated = await book_repository.update(updated_entity)

            assert updated == updated_entity
            assert updated.id == entity.id
            assert updated.isbn == entity.isbn
            assert updated.title == updated_entity.title
            assert updated.author == updated_entity.author
            assert updated.published_year == updated_entity.published_year
            assert updated.total_copies == updated_entity.total_copies
            assert updated.available_copies == updated_entity.available_copies
            assert updated.created_at == updated_entity.created_at
            assert updated.updated_at == updated_entity.updated_at

        async def test_should_raise_book_repository_exception_when_a_database_error_occurs_on_merge(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            entity = make_book_entity()
            await book_repository.save(entity)

            with patch.object(
                book_repository._session,
                "merge",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(BookRepositoryException):
                    await book_repository.update(entity)

        async def test_should_raise_book_repository_exception_when_a_database_error_occurs_on_flush(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            entity = make_book_entity()
            await book_repository.save(entity)

            with patch.object(
                book_repository._session,
                "flush",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(BookRepositoryException):
                    await book_repository.update(entity)

        async def test_should_raise_book_repository_exception_when_a_database_error_occurs_on_refresh(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            entity = make_book_entity()
            await book_repository.save(entity)

            with patch.object(
                book_repository._session,
                "refresh",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(BookRepositoryException):
                    await book_repository.update(entity)
