from collections.abc import Callable
from dataclasses import replace
from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.exceptions.loan_exception import LoanRepositoryException
from src.modules.loans.infrastructure.persistence.models.loan_model import LoanModel
from src.modules.loans.infrastructure.persistence.repositories.sqlalchemy_loan_repository_adapter import (
    SQLAlchemyLoanRepositoryAdapter,
)

LoanEntityFactory = Callable[..., LoanEntity]

pytestmark = pytest.mark.db


class TestSQLAlchemyLoanRepositoryAdapter:
    class TestExistsActiveByMemberAndBook:
        async def test_should_return_false_when_no_loan_exists(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
        ) -> None:
            assert (
                await loan_repository.exists_active_by_member_and_book(uuid4(), uuid4())
                is False
            )

        async def test_should_return_true_when_active_loan_exists(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            await loan_repository.save(entity)

            assert (
                await loan_repository.exists_active_by_member_and_book(
                    entity.member_id, entity.book_id
                )
                is True
            )

        async def test_should_return_false_when_loan_is_returned(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity(status=LoanStatusEnum.RETURNED)
            await loan_repository.save(entity)

            assert (
                await loan_repository.exists_active_by_member_and_book(
                    entity.member_id, entity.book_id
                )
                is False
            )

        async def test_should_return_false_for_other_member_or_book(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            await loan_repository.save(entity)

            assert (
                await loan_repository.exists_active_by_member_and_book(
                    uuid4(), entity.book_id
                )
                is False
            )
            assert (
                await loan_repository.exists_active_by_member_and_book(
                    entity.member_id, uuid4()
                )
                is False
            )

        async def test_should_raise_loan_repository_exception_when_a_database_error_occurs(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
        ) -> None:
            with patch.object(
                loan_repository._session,
                "execute",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(LoanRepositoryException):
                    await loan_repository.exists_active_by_member_and_book(
                        uuid4(), uuid4()
                    )

    class TestCountActiveByMember:
        async def test_should_return_zero_when_no_loans_exist(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
        ) -> None:
            assert await loan_repository.count_active_by_member(uuid4()) == 0

        async def test_should_count_only_active_loans_for_the_member(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            active_first = make_loan_entity()
            active_second = make_loan_entity(member_id=active_first.member_id)
            returned = make_loan_entity(
                member_id=active_first.member_id, status=LoanStatusEnum.RETURNED
            )
            other_member = make_loan_entity()
            await loan_repository.save(active_first)
            await loan_repository.save(active_second)
            await loan_repository.save(returned)
            await loan_repository.save(other_member)

            assert (
                await loan_repository.count_active_by_member(active_first.member_id)
                == 2
            )
            assert (
                await loan_repository.count_active_by_member(other_member.member_id)
                == 1
            )

        async def test_should_return_zero_when_member_only_has_returned_loans(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            returned = make_loan_entity(status=LoanStatusEnum.RETURNED)
            await loan_repository.save(returned)

            assert await loan_repository.count_active_by_member(returned.member_id) == 0

        async def test_should_raise_loan_repository_exception_when_a_database_error_occurs(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
        ) -> None:
            with patch.object(
                loan_repository._session,
                "execute",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(LoanRepositoryException):
                    await loan_repository.count_active_by_member(uuid4())

    class TestSave:
        async def test_should_persist_loan_when_entity_is_valid(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            db_session: AsyncSession,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()

            await loan_repository.save(entity)

            persisted = await db_session.get(LoanModel, entity.id)
            assert persisted is not None
            assert persisted.member_id == entity.member_id
            assert persisted.book_id == entity.book_id
            assert persisted.status == entity.status.value
            assert persisted.loaned_at == entity.loaned_at
            assert persisted.returned_at == entity.returned_at

        async def test_should_return_saved_entity_with_matching_attributes(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()

            saved = await loan_repository.save(entity)

            assert saved == entity
            assert saved.id == entity.id
            assert saved.member_id == entity.member_id
            assert saved.book_id == entity.book_id
            assert saved.status == entity.status
            assert saved.loaned_at == entity.loaned_at
            assert saved.returned_at == entity.returned_at
            assert saved.created_at == entity.created_at
            assert saved.updated_at == entity.updated_at

        async def test_should_raise_loan_repository_exception_when_id_already_exists(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            await loan_repository.save(entity)

            duplicate = replace(make_loan_entity(), id=entity.id)

            with pytest.raises(LoanRepositoryException):
                await loan_repository.save(duplicate)

        async def test_should_raise_loan_repository_exception_when_a_database_error_occurs_on_add(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            with patch.object(
                loan_repository._session,
                "add",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(LoanRepositoryException):
                    await loan_repository.save(make_loan_entity())

        async def test_should_raise_loan_repository_exception_when_a_database_error_occurs_on_flush(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            with patch.object(
                loan_repository._session,
                "flush",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(LoanRepositoryException):
                    await loan_repository.save(make_loan_entity())

        async def test_should_raise_loan_repository_exception_when_a_database_error_occurs_on_refresh(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            with patch.object(
                loan_repository._session,
                "refresh",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(LoanRepositoryException):
                    await loan_repository.save(make_loan_entity())
