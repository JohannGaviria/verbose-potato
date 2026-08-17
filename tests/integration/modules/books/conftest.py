from collections.abc import Callable
from datetime import date

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.value_objects.author_vo import AuthorVO
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.domain.value_objects.published_year_vo import PublishedYearVO
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.modules.books.domain.value_objects.total_copies_vo import TotalCopiesVO
from src.modules.books.infrastructure.persistence.repositories.sqlalchemy_book_repository_adapter import (
    SQLAlchemyBookRepositoryAdapter,
)
from src.modules.books.infrastructure.persistence.unit_of_work.sqlalchemy_book_unit_of_work_adapter import (
    SQLAlchemyBookUnitOfWorkAdapter,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from tests.conftest import _generate_isbn13

BookEntityFactory = Callable[..., BookEntity]


@pytest.fixture
def make_book_entity(faker: Faker) -> BookEntityFactory:
    """Factory for building a valid ``BookEntity`` with sensible fake defaults.

    Any attribute can be overridden, e.g. ``make_book_entity(total_copies=5)``.
    """

    def _make(
        *,
        title: str | None = None,
        isbn: str | None = None,
        author: str | None = None,
        published_year: int | None = None,
        total_copies: int = 3,
    ) -> BookEntity:
        return BookEntity.create(
            title=TitleVO(title or faker.sentence(nb_words=4)),
            isbn=IsbnVO(isbn or _generate_isbn13(faker)),
            author=AuthorVO(author or faker.name()),
            published_year=PublishedYearVO(
                published_year or faker.random_int(min=1450, max=date.today().year)
            ),
            total_copies=TotalCopiesVO(total_copies),
        )

    return _make


@pytest.fixture
def book_repository(
    db_session: AsyncSession,
    logger_factory_outbound: LoggerFactoryOutboundPort,
) -> SQLAlchemyBookRepositoryAdapter:
    return SQLAlchemyBookRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture
def book_unit_of_work(
    session_factory: async_sessionmaker[AsyncSession],
    logger_factory_outbound: LoggerFactoryOutboundPort,
) -> SQLAlchemyBookUnitOfWorkAdapter:
    return SQLAlchemyBookUnitOfWorkAdapter(
        session_factory=session_factory,
        logger_factory_outbound=logger_factory_outbound,
    )
