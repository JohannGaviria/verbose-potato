from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.exceptions.loan_exception import LoanRepositoryException
from src.modules.loans.domain.value_objects.member_loan_query_vo import (
    MemberLoanQueryVO,
)
from src.modules.loans.infrastructure.persistence.models.loan_model import LoanModel
from src.modules.loans.infrastructure.persistence.repositories.sqlalchemy_loan_repository_adapter import (
    SQLAlchemyLoanRepositoryAdapter,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum

LoanEntityFactory = Callable[..., LoanEntity]

pytestmark = pytest.mark.db


def _build_member_query(**overrides: Any) -> MemberLoanQueryVO:
    defaults: dict[str, Any] = {
        "status": None,
        "sort_by": None,
        "sort_order": None,
        "page": 1,
        "page_size": 20,
    }
    defaults.update(overrides)
    return MemberLoanQueryVO(**defaults)


class TestSQLAlchemyLoanRepositoryAdapter:
    class TestFindById:
        async def test_should_return_none_when_loan_does_not_exist(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
        ) -> None:
            assert await loan_repository.find_by_id(uuid4()) is None

        async def test_should_return_loan_when_loan_exists(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            await loan_repository.save(entity)

            found = await loan_repository.find_by_id(entity.id)

            assert found == entity
            assert found.id == entity.id
            assert found.member_id == entity.member_id
            assert found.book_id == entity.book_id
            assert found.status == entity.status
            assert found.loaned_at == entity.loaned_at
            assert found.returned_at == entity.returned_at

        async def test_should_return_returned_loan_when_loan_was_returned(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity(status=LoanStatusEnum.RETURNED)
            await loan_repository.save(entity)

            found = await loan_repository.find_by_id(entity.id)

            assert found is not None
            assert found.status == LoanStatusEnum.RETURNED
            assert found.returned_at == entity.returned_at

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
                    await loan_repository.find_by_id(uuid4())

    class TestUpdate:
        async def test_should_persist_updates_when_loan_entity_is_updated(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            db_session: AsyncSession,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            await loan_repository.save(entity)

            updated_entity = make_loan_entity(status=LoanStatusEnum.RETURNED)
            updated_entity = replace(
                updated_entity,
                id=entity.id,
                member_id=entity.member_id,
                book_id=entity.book_id,
            )

            await loan_repository.update(updated_entity)

            persisted = await db_session.get(LoanModel, entity.id)
            assert persisted is not None
            assert persisted.status == LoanStatusEnum.RETURNED.value
            assert persisted.returned_at is not None

        async def test_should_return_updated_entity_with_matching_attributes(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            await loan_repository.save(entity)

            updated_entity = make_loan_entity(status=LoanStatusEnum.RETURNED)
            updated_entity = replace(
                updated_entity,
                id=entity.id,
                member_id=entity.member_id,
                book_id=entity.book_id,
            )

            result = await loan_repository.update(updated_entity)

            assert result.id == entity.id
            assert result.status == LoanStatusEnum.RETURNED
            assert result.returned_at == updated_entity.returned_at

        async def test_should_insert_loan_when_loan_does_not_exist(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            db_session: AsyncSession,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity(status=LoanStatusEnum.RETURNED)

            result = await loan_repository.update(entity)

            persisted = await db_session.get(LoanModel, entity.id)
            assert persisted is not None
            assert result.id == entity.id
            assert result.status == LoanStatusEnum.RETURNED

        async def test_should_raise_loan_repository_exception_when_a_database_error_occurs(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            await loan_repository.save(entity)

            with patch.object(
                loan_repository._session,
                "flush",
                side_effect=SQLAlchemyError("boom"),
            ):
                with pytest.raises(LoanRepositoryException):
                    await loan_repository.update(entity)

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

    class TestFindByMember:
        async def test_should_return_empty_list_and_zero_total_when_no_loans_exist(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
        ) -> None:
            loans, total = await loan_repository.find_by_member(
                uuid4(), _build_member_query()
            )

            assert loans == []
            assert total == 0

        async def test_should_return_all_loans_and_total_when_no_filters_are_provided(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            member_id = entity.member_id
            first = make_loan_entity(member_id=member_id)
            second = make_loan_entity(member_id=member_id)
            other = make_loan_entity()
            await loan_repository.save(first)
            await loan_repository.save(second)
            await loan_repository.save(other)

            loans, total = await loan_repository.find_by_member(
                member_id, _build_member_query()
            )

            assert total == 2
            assert {loan.id for loan in loans} == {first.id, second.id}

        async def test_should_return_only_loans_belonging_to_the_member(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            member_id = entity.member_id
            await loan_repository.save(entity)
            await loan_repository.save(make_loan_entity())
            await loan_repository.save(make_loan_entity())

            loans, total = await loan_repository.find_by_member(
                member_id, _build_member_query()
            )

            assert total == 1
            assert [loan.id for loan in loans] == [entity.id]

        async def test_should_filter_by_active_status(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            member_id = entity.member_id
            active = make_loan_entity(member_id=member_id)
            returned = make_loan_entity(
                member_id=member_id, status=LoanStatusEnum.RETURNED
            )
            await loan_repository.save(active)
            await loan_repository.save(returned)

            query = _build_member_query(status=LoanStatusEnum.ACTIVE)
            loans, total = await loan_repository.find_by_member(member_id, query)

            assert total == 1
            assert [loan.id for loan in loans] == [active.id]

        async def test_should_filter_by_returned_status(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            member_id = entity.member_id
            active = make_loan_entity(member_id=member_id)
            returned = make_loan_entity(
                member_id=member_id, status=LoanStatusEnum.RETURNED
            )
            await loan_repository.save(active)
            await loan_repository.save(returned)

            query = _build_member_query(status=LoanStatusEnum.RETURNED)
            loans, total = await loan_repository.find_by_member(member_id, query)

            assert total == 1
            assert [loan.id for loan in loans] == [returned.id]

        async def test_should_return_empty_list_when_no_loan_matches_filters(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            await loan_repository.save(entity)

            query = _build_member_query(status=LoanStatusEnum.RETURNED)
            loans, total = await loan_repository.find_by_member(entity.member_id, query)

            assert loans == []
            assert total == 0

        async def test_should_sort_by_loaned_at_ascending(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            member_id = entity.member_id
            base = datetime.now(UTC)
            older = replace(
                make_loan_entity(member_id=member_id),
                loaned_at=base - timedelta(days=10),
            )
            newer = replace(
                make_loan_entity(member_id=member_id),
                loaned_at=base - timedelta(days=1),
            )
            await loan_repository.save(older)
            await loan_repository.save(newer)

            query = _build_member_query(
                sort_by=LoanSortByEnum.LOANED_AT,
                sort_order=SortOrderEnum.ASC,
            )
            loans, _ = await loan_repository.find_by_member(member_id, query)

            assert [loan.id for loan in loans] == [older.id, newer.id]

        async def test_should_sort_by_loaned_at_descending(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            member_id = entity.member_id
            base = datetime.now(UTC)
            older = replace(
                make_loan_entity(member_id=member_id),
                loaned_at=base - timedelta(days=10),
            )
            newer = replace(
                make_loan_entity(member_id=member_id),
                loaned_at=base - timedelta(days=1),
            )
            await loan_repository.save(older)
            await loan_repository.save(newer)

            query = _build_member_query(
                sort_by=LoanSortByEnum.LOANED_AT,
                sort_order=SortOrderEnum.DESC,
            )
            loans, _ = await loan_repository.find_by_member(member_id, query)

            assert [loan.id for loan in loans] == [newer.id, older.id]

        async def test_should_sort_by_returned_at_ascending(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            member_id = entity.member_id
            base = datetime.now(UTC)
            older = make_loan_entity(
                member_id=member_id,
                status=LoanStatusEnum.RETURNED,
                returned_at=base - timedelta(days=10),
            )
            newer = make_loan_entity(
                member_id=member_id,
                status=LoanStatusEnum.RETURNED,
                returned_at=base - timedelta(days=1),
            )
            await loan_repository.save(older)
            await loan_repository.save(newer)

            query = _build_member_query(
                sort_by=LoanSortByEnum.RETURNED_AT,
                sort_order=SortOrderEnum.ASC,
            )
            loans, _ = await loan_repository.find_by_member(member_id, query)

            assert [loan.id for loan in loans] == [older.id, newer.id]

        async def test_should_sort_by_returned_at_descending(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            member_id = entity.member_id
            base = datetime.now(UTC)
            older = make_loan_entity(
                member_id=member_id,
                status=LoanStatusEnum.RETURNED,
                returned_at=base - timedelta(days=10),
            )
            newer = make_loan_entity(
                member_id=member_id,
                status=LoanStatusEnum.RETURNED,
                returned_at=base - timedelta(days=1),
            )
            await loan_repository.save(older)
            await loan_repository.save(newer)

            query = _build_member_query(
                sort_by=LoanSortByEnum.RETURNED_AT,
                sort_order=SortOrderEnum.DESC,
            )
            loans, _ = await loan_repository.find_by_member(member_id, query)

            assert [loan.id for loan in loans] == [newer.id, older.id]

        async def test_should_paginate_results_across_multiple_pages(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            member_id = entity.member_id
            created = [
                replace(
                    make_loan_entity(member_id=member_id),
                    loaned_at=datetime.now(UTC) + timedelta(days=index),
                )
                for index in range(5)
            ]
            for entity in created:
                await loan_repository.save(entity)

            expected_order = sorted(created, key=lambda loan: loan.loaned_at)

            first_page, total = await loan_repository.find_by_member(
                member_id,
                _build_member_query(
                    sort_by=LoanSortByEnum.LOANED_AT,
                    sort_order=SortOrderEnum.ASC,
                    page=1,
                    page_size=2,
                ),
            )
            second_page, _ = await loan_repository.find_by_member(
                member_id,
                _build_member_query(
                    sort_by=LoanSortByEnum.LOANED_AT,
                    sort_order=SortOrderEnum.ASC,
                    page=2,
                    page_size=2,
                ),
            )
            third_page, _ = await loan_repository.find_by_member(
                member_id,
                _build_member_query(
                    sort_by=LoanSortByEnum.LOANED_AT,
                    sort_order=SortOrderEnum.ASC,
                    page=3,
                    page_size=2,
                ),
            )

            assert total == 5
            assert len(first_page) == 2
            assert len(second_page) == 2
            assert len(third_page) == 1

            paginated_ids = [loan.id for loan in first_page + second_page + third_page]
            assert paginated_ids == [loan.id for loan in expected_order]

        async def test_should_return_empty_list_when_page_is_beyond_available_results(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity()
            await loan_repository.save(entity)

            loans, total = await loan_repository.find_by_member(
                entity.member_id,
                _build_member_query(page=2, page_size=20),
            )

            assert loans == []
            assert total == 1

        async def test_should_map_persisted_loans_to_loan_entities(
            self,
            loan_repository: SQLAlchemyLoanRepositoryAdapter,
            make_loan_entity: LoanEntityFactory,
        ) -> None:
            entity = make_loan_entity(status=LoanStatusEnum.RETURNED)
            await loan_repository.save(entity)

            loans, _ = await loan_repository.find_by_member(
                entity.member_id, _build_member_query()
            )

            assert len(loans) == 1
            found = loans[0]
            assert found.id == entity.id
            assert found.member_id == entity.member_id
            assert found.book_id == entity.book_id
            assert found.status == entity.status
            assert found.loaned_at == entity.loaned_at
            assert found.returned_at == entity.returned_at
            assert found.created_at == entity.created_at
            assert found.updated_at == entity.updated_at

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
                    await loan_repository.find_by_member(uuid4(), _build_member_query())
