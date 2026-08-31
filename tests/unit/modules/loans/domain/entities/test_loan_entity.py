from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest
from faker import Faker

from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum


def _build_loan_entity(faker: Faker) -> LoanEntity:
    return LoanEntity.create(
        member_id=faker.uuid4(cast_to=None),
        book_id=faker.uuid4(cast_to=None),
    )


class TestLoanEntity:
    def test_should_create_loan_entity_when_member_id_and_book_id_are_provided(
        self, faker: Faker
    ) -> None:
        member_id = faker.uuid4(cast_to=None)
        book_id = faker.uuid4(cast_to=None)

        loan = LoanEntity.create(member_id=member_id, book_id=book_id)

        assert loan.id is not None
        assert loan.member_id == member_id
        assert loan.book_id == book_id

    def test_should_set_status_to_active_on_creation(self, faker: Faker) -> None:
        loan = _build_loan_entity(faker)

        assert loan.status == LoanStatusEnum.ACTIVE

    def test_should_set_returned_at_to_none_on_creation(self, faker: Faker) -> None:
        loan = _build_loan_entity(faker)

        assert loan.returned_at is None

    def test_should_set_loaned_at_created_at_and_updated_at_to_the_same_timestamp(
        self, faker: Faker
    ) -> None:
        loan = _build_loan_entity(faker)

        assert loan.loaned_at == loan.created_at
        assert loan.created_at == loan.updated_at

    def test_should_return_correct_types_for_loan_entity_attributes(
        self, faker: Faker
    ) -> None:
        loan = _build_loan_entity(faker)

        assert isinstance(loan.status, LoanStatusEnum)
        assert loan.returned_at is None or isinstance(
            loan.returned_at, type(loan.loaned_at)
        )

    def test_should_generate_a_unique_id_for_each_created_loan(
        self, faker: Faker
    ) -> None:
        loan1 = _build_loan_entity(faker)
        loan2 = _build_loan_entity(faker)

        assert loan1.id != loan2.id

    def test_should_raise_exception_when_attempting_to_modify_loan_entity_status(
        self, faker: Faker
    ) -> None:
        loan = _build_loan_entity(faker)

        with pytest.raises(FrozenInstanceError):
            loan.status = LoanStatusEnum.RETURNED  # type: ignore[misc]

    def test_should_return_equal_loan_entities_when_data_is_identical(
        self, faker: Faker
    ) -> None:
        loan1 = _build_loan_entity(faker)
        loan2 = LoanEntity(
            id=loan1.id,
            member_id=loan1.member_id,
            book_id=loan1.book_id,
            status=loan1.status,
            loaned_at=loan1.loaned_at,
            returned_at=loan1.returned_at,
            created_at=loan1.created_at,
            updated_at=loan1.updated_at,
        )

        assert loan1 == loan2

    def test_should_return_different_loan_entities_when_ids_differ(
        self, faker: Faker
    ) -> None:
        loan1 = _build_loan_entity(faker)
        loan2 = _build_loan_entity(faker)

        assert loan1 != loan2


class TestLoanEntityMarkReturned:
    def test_should_set_status_to_returned_when_mark_returned_is_called(
        self, faker: Faker
    ) -> None:
        loan = _build_loan_entity(faker)

        returned_loan = loan.mark_returned()

        assert returned_loan.status == LoanStatusEnum.RETURNED

    def test_should_set_returned_at_when_mark_returned_is_called(
        self, faker: Faker
    ) -> None:
        loan = _build_loan_entity(faker)

        returned_loan = loan.mark_returned()

        assert returned_loan.returned_at is not None
        assert isinstance(returned_loan.returned_at, datetime)

    def test_should_update_updated_at_when_mark_returned_is_called(
        self, faker: Faker
    ) -> None:
        loan = _build_loan_entity(faker)

        returned_loan = loan.mark_returned()

        assert returned_loan.updated_at >= loan.updated_at

    def test_should_return_new_instance_when_mark_returned_is_called(
        self, faker: Faker
    ) -> None:
        loan = _build_loan_entity(faker)

        returned_loan = loan.mark_returned()

        assert loan is not returned_loan
        assert loan.id == returned_loan.id
        assert loan.member_id == returned_loan.member_id
        assert loan.book_id == returned_loan.book_id
        assert loan.loaned_at == returned_loan.loaned_at

    def test_should_not_modify_original_entity_when_mark_returned_is_called(
        self, faker: Faker
    ) -> None:
        loan = _build_loan_entity(faker)

        _ = loan.mark_returned()

        assert loan.status == LoanStatusEnum.ACTIVE
        assert loan.returned_at is None
