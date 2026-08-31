from collections.abc import Callable
from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.exceptions.book_exception import BookRepositoryException
from src.modules.books.infrastructure.persistence.models.book_model import BookModel
from src.modules.books.infrastructure.persistence.repositories.sqlalchemy_book_availability_repository_adapter import (
    SQLAlchemyBookAvailabilityRepositoryAdapter,
)
from src.modules.books.infrastructure.persistence.repositories.sqlalchemy_book_repository_adapter import (
    SQLAlchemyBookRepositoryAdapter,
)
from src.modules.loans.domain.value_objects.book_availability_reference_vo import (
    BookAvailabilityReferenceVO,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)

BookEntityFactory = Callable[..., BookEntity]

pytestmark = pytest.mark.db


@pytest.fixture
def book_availability_repository(
    db_session: AsyncSession,
    logger_factory_outbound: LoggerFactoryOutboundPort,
) -> SQLAlchemyBookAvailabilityRepositoryAdapter:
    return SQLAlchemyBookAvailabilityRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


class TestSQLAlchemyBookAvailabilityRepositoryAdapter:
    class TestFindById:
        async def test_should_return_none_when_book_does_not_exist(
            self,
            book_availability_repository: SQLAlchemyBookAvailabilityRepositoryAdapter,
        ) -> None:
            assert await book_availability_repository.find_by_id(uuid4()) is None

        async def test_should_return_book_availability_reference_when_book_exists(
            self,
            book_availability_repository: SQLAlchemyBookAvailabilityRepositoryAdapter,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            book = make_book_entity(total_copies=3)
            await book_repository.save(book)

            availability = await book_availability_repository.find_by_id(book.id)

            assert availability == BookAvailabilityReferenceVO(
                book_id=book.id,
                available_copies=3,
            )

        async def test_should_raise_book_repository_exception_when_a_database_error_occurs(
            self,
            book_availability_repository: SQLAlchemyBookAvailabilityRepositoryAdapter,
        ) -> None:
            with patch.object(
                book_availability_repository._session,
                "execute",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(BookRepositoryException):
                    await book_availability_repository.find_by_id(uuid4())

    class TestUpdateAvailableCopies:
        async def test_should_update_available_copies_when_book_exists(
            self,
            book_availability_repository: SQLAlchemyBookAvailabilityRepositoryAdapter,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            db_session: AsyncSession,
            make_book_entity: BookEntityFactory,
        ) -> None:
            book = make_book_entity(total_copies=3)
            await book_repository.save(book)

            await book_availability_repository.update_available_copies(book.id, 2)

            stmt = select(BookModel.available_copies).where(BookModel.id == book.id)
            result = await db_session.execute(stmt)
            assert result.scalar_one() == 2

        async def test_should_expose_updated_copies_through_find_by_id(
            self,
            book_availability_repository: SQLAlchemyBookAvailabilityRepositoryAdapter,
            book_repository: SQLAlchemyBookRepositoryAdapter,
            make_book_entity: BookEntityFactory,
        ) -> None:
            book = make_book_entity(total_copies=3)
            await book_repository.save(book)

            await book_availability_repository.update_available_copies(book.id, 1)

            availability = await book_availability_repository.find_by_id(book.id)
            assert availability is not None
            assert availability.available_copies == 1

        async def test_should_be_a_noop_when_book_does_not_exist(
            self,
            book_availability_repository: SQLAlchemyBookAvailabilityRepositoryAdapter,
        ) -> None:
            await book_availability_repository.update_available_copies(uuid4(), 0)

        async def test_should_raise_book_repository_exception_when_a_database_error_occurs(
            self,
            book_availability_repository: SQLAlchemyBookAvailabilityRepositoryAdapter,
        ) -> None:
            with patch.object(
                book_availability_repository._session,
                "execute",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(BookRepositoryException):
                    await book_availability_repository.update_available_copies(
                        uuid4(), 0
                    )
