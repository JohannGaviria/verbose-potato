from collections.abc import Callable
from dataclasses import replace
from typing import Any
from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.enums.book_catalog_sort_by_enum import (
    BookCatalogSortByEnum,
)
from src.modules.books.domain.exceptions.book_exception import BookRepositoryException
from src.modules.books.domain.value_objects.author_vo import AuthorVO
from src.modules.books.domain.value_objects.book_catalog_query_vo import (
    BookCatalogQueryVO,
)
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.domain.value_objects.published_year_vo import PublishedYearVO
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.modules.books.domain.value_objects.total_copies_vo import TotalCopiesVO
from src.modules.books.infrastructure.persistence.models.book_model import BookModel
from src.modules.books.infrastructure.persistence.repositories.sqlalchemy_book_repository_adapter import (
    SQLAlchemyBookRepositoryAdapter,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum

BookEntityFactory = Callable[..., BookEntity]

pytestmark = pytest.mark.db


def _build_query(**overrides: Any) -> BookCatalogQueryVO:
    defaults: dict[str, Any] = {
        "title": None,
        "author": None,
        "isbn": None,
        "is_available": None,
        "sort_by": None,
        "sort_order": None,
        "page": 1,
        "page_size": 20,
    }
    defaults.update(overrides)
    return BookCatalogQueryVO(**defaults)


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

    class TestFindCatalog:
        async def test_should_return_empty_list_and_zero_total_when_no_books_exist(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
        ) -> None:
            books, total = await book_repository.find_catalog(_build_query())

            assert books == []
            assert total == 0

        async def test_should_return_all_books_and_total_when_no_filters_are_provided(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            first = make_book_entity()
            second = make_book_entity()
            await book_repository.save(first)
            await book_repository.save(second)

            books, total = await book_repository.find_catalog(_build_query())

            assert total == 2
            assert {book.id for book in books} == {first.id, second.id}

        async def test_should_filter_by_title_case_insensitively_and_partially(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            target = make_book_entity(title="Clean Architecture")
            other = make_book_entity(title="Refactoring")
            await book_repository.save(target)
            await book_repository.save(other)

            query = _build_query(title=TitleVO("clean"))
            books, total = await book_repository.find_catalog(query)

            assert total == 1
            assert [book.id for book in books] == [target.id]

        async def test_should_filter_by_author_case_insensitively_and_partially(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            target = make_book_entity(author="Robert Martin")
            other = make_book_entity(author="Martin Fowler")
            await book_repository.save(target)
            await book_repository.save(other)

            query = _build_query(author=AuthorVO("robert"))
            books, total = await book_repository.find_catalog(query)

            assert total == 1
            assert [book.id for book in books] == [target.id]

        async def test_should_filter_by_exact_isbn(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            target_isbn = "9780306406157"
            other_isbn = "9780132350884"
            target = make_book_entity(isbn=target_isbn)
            other = make_book_entity(isbn=other_isbn)
            await book_repository.save(target)
            await book_repository.save(other)

            query = _build_query(isbn=IsbnVO(target_isbn))
            books, total = await book_repository.find_catalog(query)

            assert total == 1
            assert [book.id for book in books] == [target.id]

        async def test_should_return_only_available_books_when_is_available_filter_is_true(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            available = make_book_entity(total_copies=3)
            unavailable = replace(make_book_entity(total_copies=2), available_copies=0)
            await book_repository.save(available)
            await book_repository.save(unavailable)

            query = _build_query(is_available=True)
            books, total = await book_repository.find_catalog(query)

            assert total == 1
            assert [book.id for book in books] == [available.id]

        async def test_should_ignore_is_available_filter_when_it_is_false_or_none(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            available = make_book_entity(total_copies=3)
            unavailable = replace(make_book_entity(total_copies=2), available_copies=0)
            await book_repository.save(available)
            await book_repository.save(unavailable)

            books, total = await book_repository.find_catalog(
                _build_query(is_available=None)
            )

            assert total == 2
            assert {book.id for book in books} == {available.id, unavailable.id}

        async def test_should_combine_title_author_and_availability_filters(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            match = make_book_entity(
                title="Domain Driven Design", author="Eric Evans", total_copies=3
            )
            wrong_title = make_book_entity(
                title="Refactoring", author="Eric Evans", total_copies=3
            )
            unavailable_match = replace(
                make_book_entity(
                    title="Domain Driven Design Distilled",
                    author="Eric Evans",
                    total_copies=2,
                ),
                available_copies=0,
            )
            await book_repository.save(match)
            await book_repository.save(wrong_title)
            await book_repository.save(unavailable_match)

            query = _build_query(
                title=TitleVO("Domain Driven"),
                author=AuthorVO("Eric Evans"),
                is_available=True,
            )
            books, total = await book_repository.find_catalog(query)

            assert total == 1
            assert [book.id for book in books] == [match.id]

        async def test_should_return_empty_list_when_no_book_matches_filters(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            await book_repository.save(make_book_entity(title="Clean Code"))

            query = _build_query(title=TitleVO("Nonexistent"))
            books, total = await book_repository.find_catalog(query)

            assert books == []
            assert total == 0

        async def test_should_sort_by_title_ascending(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            second = make_book_entity(title="Banana Bread")
            first = make_book_entity(title="Apple Pie")
            await book_repository.save(second)
            await book_repository.save(first)

            query = _build_query(
                sort_by=BookCatalogSortByEnum.TITLE, sort_order=SortOrderEnum.ASC
            )
            books, _ = await book_repository.find_catalog(query)

            assert [book.id for book in books] == [first.id, second.id]

        async def test_should_sort_by_title_descending(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            first = make_book_entity(title="Apple Pie")
            second = make_book_entity(title="Banana Bread")
            await book_repository.save(first)
            await book_repository.save(second)

            query = _build_query(
                sort_by=BookCatalogSortByEnum.TITLE, sort_order=SortOrderEnum.DESC
            )
            books, _ = await book_repository.find_catalog(query)

            assert [book.id for book in books] == [second.id, first.id]

        async def test_should_sort_by_published_year_ascending(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            newer = make_book_entity(published_year=2020)
            older = make_book_entity(published_year=1999)
            await book_repository.save(newer)
            await book_repository.save(older)

            query = _build_query(
                sort_by=BookCatalogSortByEnum.PUBLISHED_YEAR,
                sort_order=SortOrderEnum.ASC,
            )
            books, _ = await book_repository.find_catalog(query)

            assert [book.id for book in books] == [older.id, newer.id]

        async def test_should_sort_by_published_year_descending(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            older = make_book_entity(published_year=1999)
            newer = make_book_entity(published_year=2020)
            await book_repository.save(older)
            await book_repository.save(newer)

            query = _build_query(
                sort_by=BookCatalogSortByEnum.PUBLISHED_YEAR,
                sort_order=SortOrderEnum.DESC,
            )
            books, _ = await book_repository.find_catalog(query)

            assert [book.id for book in books] == [newer.id, older.id]

        async def test_should_paginate_results_across_multiple_pages(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            created = [
                make_book_entity(title=f"Book {index:02d}") for index in range(5)
            ]
            for entity in created:
                await book_repository.save(entity)

            expected_order = sorted(created, key=lambda entity: entity.title.value)

            first_page, total = await book_repository.find_catalog(
                _build_query(
                    sort_by=BookCatalogSortByEnum.TITLE,
                    sort_order=SortOrderEnum.ASC,
                    page=1,
                    page_size=2,
                )
            )
            second_page, _ = await book_repository.find_catalog(
                _build_query(
                    sort_by=BookCatalogSortByEnum.TITLE,
                    sort_order=SortOrderEnum.ASC,
                    page=2,
                    page_size=2,
                )
            )
            third_page, _ = await book_repository.find_catalog(
                _build_query(
                    sort_by=BookCatalogSortByEnum.TITLE,
                    sort_order=SortOrderEnum.ASC,
                    page=3,
                    page_size=2,
                )
            )

            assert total == 5
            assert len(first_page) == 2
            assert len(second_page) == 2
            assert len(third_page) == 1

            paginated_ids = [book.id for book in first_page + second_page + third_page]
            assert paginated_ids == [entity.id for entity in expected_order]

        async def test_should_return_empty_list_when_page_is_beyond_available_results(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            await book_repository.save(make_book_entity())

            books, total = await book_repository.find_catalog(
                _build_query(page=2, page_size=20)
            )

            assert books == []
            assert total == 1

        async def test_should_map_persisted_books_to_book_entities(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            entity = make_book_entity(total_copies=5)
            await book_repository.save(entity)

            books, _ = await book_repository.find_catalog(_build_query())

            assert len(books) == 1
            found = books[0]
            assert found.id == entity.id
            assert found.title == entity.title
            assert found.isbn == entity.isbn
            assert found.author == entity.author
            assert found.published_year == entity.published_year
            assert found.total_copies == entity.total_copies
            assert found.available_copies == entity.available_copies
            assert found.created_at == entity.created_at
            assert found.updated_at == entity.updated_at

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
                    await book_repository.find_catalog(_build_query())

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

    class TestDelete:
        async def test_should_remove_book_when_book_exists(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            db_session: AsyncSession,
            make_book_entity: BookEntityFactory,
        ) -> None:
            entity = make_book_entity()
            await book_repository.save(entity)

            await book_repository.delete(entity.id)

            persisted = await db_session.get(BookModel, entity.id)
            assert persisted is None

        async def test_should_not_affect_other_books_when_deleting_one_book(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            db_session: AsyncSession,
            make_book_entity: BookEntityFactory,
        ) -> None:
            entity_to_delete = make_book_entity()
            entity_to_keep = make_book_entity()
            await book_repository.save(entity_to_delete)
            await book_repository.save(entity_to_keep)

            await book_repository.delete(entity_to_delete.id)

            assert await db_session.get(BookModel, entity_to_delete.id) is None
            assert await db_session.get(BookModel, entity_to_keep.id) is not None

        async def test_should_not_raise_when_book_does_not_exist(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
        ) -> None:
            await book_repository.delete(uuid4())

        async def test_should_raise_book_repository_exception_when_a_database_error_occurs_on_execute(
            self,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            entity = make_book_entity()
            await book_repository.save(entity)

            with patch.object(
                book_repository._session,
                "execute",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(BookRepositoryException):
                    await book_repository.delete(entity.id)

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
                    await book_repository.delete(entity.id)
