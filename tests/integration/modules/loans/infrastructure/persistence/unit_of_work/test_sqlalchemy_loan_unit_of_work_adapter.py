from collections.abc import Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.infrastructure.persistence.models.book_model import BookModel
from src.modules.books.infrastructure.persistence.repositories.sqlalchemy_book_availability_repository_adapter import (
    SQLAlchemyBookAvailabilityRepositoryAdapter,
)
from src.modules.books.infrastructure.persistence.repositories.sqlalchemy_book_repository_adapter import (
    SQLAlchemyBookRepositoryAdapter,
)
from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.infrastructure.persistence.models.loan_model import LoanModel
from src.modules.loans.infrastructure.persistence.repositories.sqlalchemy_loan_repository_adapter import (
    SQLAlchemyLoanRepositoryAdapter,
)
from src.modules.loans.infrastructure.persistence.unit_of_work.sqlalchemy_loan_unit_of_work_adapter import (
    SQLAlchemyLoanUnitOfWorkAdapter,
)

BookEntityFactory = Callable[..., BookEntity]
LoanEntityFactory = Callable[..., LoanEntity]

pytestmark = pytest.mark.db


class TestSQLAlchemyLoanUnitOfWorkAdapter:
    async def test_should_expose_repositories_when_context_is_entered(
        self,
        loan_unit_of_work: SQLAlchemyLoanUnitOfWorkAdapter,
    ) -> None:
        async with loan_unit_of_work as uow:
            assert isinstance(uow.loans, SQLAlchemyLoanRepositoryAdapter)
            assert isinstance(
                uow.book_availability, SQLAlchemyBookAvailabilityRepositoryAdapter
            )

    async def test_should_persist_loan_and_book_availability_atomically_on_commit(
        self,
        loan_unit_of_work: SQLAlchemyLoanUnitOfWorkAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        book_repository: SQLAlchemyBookRepositoryAdapter,
        make_book_entity: BookEntityFactory,
        make_loan_entity: LoanEntityFactory,
    ) -> None:
        book = make_book_entity(total_copies=3)
        await book_repository.save(book)
        loan = make_loan_entity(book_id=book.id)

        async with loan_unit_of_work as uow:
            availability = await uow.book_availability.find_by_id(book.id)
            assert availability is not None
            assert availability.available_copies == 3

            reduced = availability.reduce_available_copies()
            await uow.book_availability.update_available_copies(book.id, reduced)
            await uow.loans.save(loan)
            await uow.commit()

        async with session_factory() as verification_session:
            persisted_loan = await verification_session.get(LoanModel, loan.id)
            assert persisted_loan is not None
            assert persisted_loan.status == loan.status.value

            persisted_book = await verification_session.get(BookModel, book.id)
            assert persisted_book is not None
            assert persisted_book.available_copies == 2

    async def test_should_not_persist_changes_when_commit_is_not_called(
        self,
        loan_unit_of_work: SQLAlchemyLoanUnitOfWorkAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        book_repository: SQLAlchemyBookRepositoryAdapter,
        make_book_entity: BookEntityFactory,
        make_loan_entity: LoanEntityFactory,
    ) -> None:
        book = make_book_entity(total_copies=3)
        await book_repository.save(book)
        loan = make_loan_entity(book_id=book.id)

        async with loan_unit_of_work as uow:
            availability = await uow.book_availability.find_by_id(book.id)
            assert availability is not None
            reduced = availability.reduce_available_copies()
            await uow.book_availability.update_available_copies(book.id, reduced)
            await uow.loans.save(loan)

        async with session_factory() as verification_session:
            assert await verification_session.get(LoanModel, loan.id) is None

            persisted_book = await verification_session.get(BookModel, book.id)
            assert persisted_book is not None
            assert persisted_book.available_copies == 3

    async def test_should_rollback_changes_when_exception_escapes_the_block(
        self,
        loan_unit_of_work: SQLAlchemyLoanUnitOfWorkAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        book_repository: SQLAlchemyBookRepositoryAdapter,
        make_book_entity: BookEntityFactory,
        make_loan_entity: LoanEntityFactory,
    ) -> None:
        book = make_book_entity(total_copies=3)
        await book_repository.save(book)
        loan = make_loan_entity(book_id=book.id)

        with pytest.raises(RuntimeError):
            async with loan_unit_of_work as uow:
                availability = await uow.book_availability.find_by_id(book.id)
                assert availability is not None
                reduced = availability.reduce_available_copies()
                await uow.book_availability.update_available_copies(book.id, reduced)
                await uow.loans.save(loan)
                raise RuntimeError("simulated use case failure")

        async with session_factory() as verification_session:
            assert await verification_session.get(LoanModel, loan.id) is None

            persisted_book = await verification_session.get(BookModel, book.id)
            assert persisted_book is not None
            assert persisted_book.available_copies == 3

    async def test_should_discard_changes_when_rollback_is_called_explicitly(
        self,
        loan_unit_of_work: SQLAlchemyLoanUnitOfWorkAdapter,
        session_factory: async_sessionmaker[AsyncSession],
        book_repository: SQLAlchemyBookRepositoryAdapter,
        make_book_entity: BookEntityFactory,
        make_loan_entity: LoanEntityFactory,
    ) -> None:
        book = make_book_entity(total_copies=3)
        await book_repository.save(book)
        loan = make_loan_entity(book_id=book.id)

        async with loan_unit_of_work as uow:
            availability = await uow.book_availability.find_by_id(book.id)
            assert availability is not None
            reduced = availability.reduce_available_copies()
            await uow.book_availability.update_available_copies(book.id, reduced)
            await uow.loans.save(loan)
            await uow.rollback()

        async with session_factory() as verification_session:
            assert await verification_session.get(LoanModel, loan.id) is None

            persisted_book = await verification_session.get(BookModel, book.id)
            assert persisted_book is not None
            assert persisted_book.available_copies == 3

    async def test_should_provide_a_fresh_session_on_each_use(
        self,
        loan_unit_of_work: SQLAlchemyLoanUnitOfWorkAdapter,
    ) -> None:
        async with loan_unit_of_work as first_use:
            first_session = first_use._session

        async with loan_unit_of_work as second_use:
            second_session = second_use._session

        assert first_session is not second_session

    async def test_should_raise_runtime_error_when_commit_called_outside_context(
        self,
        loan_unit_of_work: SQLAlchemyLoanUnitOfWorkAdapter,
    ) -> None:
        with pytest.raises(RuntimeError):
            await loan_unit_of_work.commit()

    async def test_should_raise_runtime_error_when_rollback_called_outside_context(
        self,
        loan_unit_of_work: SQLAlchemyLoanUnitOfWorkAdapter,
    ) -> None:
        with pytest.raises(RuntimeError):
            await loan_unit_of_work.rollback()
