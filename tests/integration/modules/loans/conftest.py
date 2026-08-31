from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

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
from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.infrastructure.persistence.repositories.sqlalchemy_loan_repository_adapter import (
    SQLAlchemyLoanRepositoryAdapter,
)
from src.modules.loans.infrastructure.persistence.unit_of_work.sqlalchemy_loan_unit_of_work_adapter import (
    SQLAlchemyLoanUnitOfWorkAdapter,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from tests.conftest import _generate_isbn13

LoanEntityFactory = Callable[..., LoanEntity]
BookEntityFactory = Callable[..., BookEntity]


@pytest.fixture
def make_loan_entity(faker: Faker) -> LoanEntityFactory:
    """Factory for building an ``LoanEntity`` with sensible fake defaults.

    Any attribute can be overridden, e.g. ``make_loan_entity(status=RETURNED)``.
    """

    def _make(
        *,
        member_id: UUID | None = None,
        book_id: UUID | None = None,
        status: LoanStatusEnum = LoanStatusEnum.ACTIVE,
        returned_at: datetime | None = None,
    ) -> LoanEntity:
        entity = LoanEntity.create(
            member_id=member_id or uuid4(),
            book_id=book_id or uuid4(),
        )
        if status is not LoanStatusEnum.ACTIVE or returned_at is not None:
            returned_at = (
                returned_at
                if returned_at is not None
                else entity.loaned_at + timedelta(days=1)
            )
            entity = replace(entity, status=status, returned_at=returned_at)
        return entity

    return _make


@pytest.fixture
def make_book_entity(faker: Faker) -> BookEntityFactory:
    """Factory for building a valid ``BookEntity`` to seed loan scenarios."""

    def _make(*, total_copies: int = 3) -> BookEntity:
        return BookEntity.create(
            title=TitleVO(faker.sentence(nb_words=4)),
            isbn=IsbnVO(_generate_isbn13(faker)),
            author=AuthorVO(faker.name()),
            published_year=PublishedYearVO(
                faker.random_int(min=1450, max=datetime.now(UTC).year)
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
def loan_repository(
    db_session: AsyncSession,
    logger_factory_outbound: LoggerFactoryOutboundPort,
) -> SQLAlchemyLoanRepositoryAdapter:
    return SQLAlchemyLoanRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture
def loan_unit_of_work(
    session_factory: async_sessionmaker[AsyncSession],
    logger_factory_outbound: LoggerFactoryOutboundPort,
) -> SQLAlchemyLoanUnitOfWorkAdapter:
    return SQLAlchemyLoanUnitOfWorkAdapter(
        session_factory=session_factory,
        logger_factory_outbound=logger_factory_outbound,
    )
