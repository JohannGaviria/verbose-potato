from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.loans.application.dtos.returning_loan_dto import (
    ReturningLoanCommandDto,
    ReturningLoanResponseDto,
)
from src.modules.loans.application.use_cases.returning_loan_use_case import (
    ReturningLoanUseCase,
)
from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.exceptions.loan_exception import (
    LoanAlreadyReturnedException,
    LoanNotFoundException,
)
from src.modules.loans.domain.value_objects.book_availability_reference_vo import (
    BookAvailabilityReferenceVO,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.authentication_authorization_exception import (
    InsufficientPermissionsException,
)


def _build_command(
    faker: Faker, loan_id: UUID | None = None
) -> ReturningLoanCommandDto:
    return ReturningLoanCommandDto(loan_id=loan_id or faker.uuid4(cast_to=None))


def _build_authenticated_user(
    faker: Faker, role: UserRoleEnum = UserRoleEnum.MEMBER
) -> AuthenticatedUserCommandDto:
    return AuthenticatedUserCommandDto(id=faker.uuid4(cast_to=None), role=role)


def _build_active_loan(
    faker: Faker,
    member_id: UUID | None = None,
    book_id: UUID | None = None,
) -> LoanEntity:
    now = datetime.now(UTC)
    return LoanEntity(
        id=faker.uuid4(cast_to=None),
        member_id=member_id or faker.uuid4(cast_to=None),
        book_id=book_id or faker.uuid4(cast_to=None),
        status=LoanStatusEnum.ACTIVE,
        loaned_at=now,
        returned_at=None,
        created_at=now,
        updated_at=now,
    )


def _build_returned_loan(
    faker: Faker,
    member_id: UUID | None = None,
    book_id: UUID | None = None,
) -> LoanEntity:
    now = datetime.now(UTC)
    return LoanEntity(
        id=faker.uuid4(cast_to=None),
        member_id=member_id or faker.uuid4(cast_to=None),
        book_id=book_id or faker.uuid4(cast_to=None),
        status=LoanStatusEnum.RETURNED,
        loaned_at=now,
        returned_at=now,
        created_at=now,
        updated_at=now,
    )


def _build_book_availability(
    book_id: UUID, available_copies: int = 2
) -> BookAvailabilityReferenceVO:
    return BookAvailabilityReferenceVO(
        book_id=book_id, available_copies=available_copies
    )


class TestReturningLoanUseCase:
    @pytest.mark.asyncio
    async def test_should_return_loan_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        loan_cache_invalidation_outbound_mock: AsyncMock,
    ) -> None:
        authenticated_user = _build_authenticated_user(faker)
        loan = _build_active_loan(faker, member_id=authenticated_user.id)
        command = _build_command(faker, loan_id=loan.id)
        book_availability = _build_book_availability(loan.book_id, available_copies=2)

        loan_unit_of_work_mock.loans.find_by_id.return_value = loan
        loan_unit_of_work_mock.book_availability.find_by_id.return_value = (
            book_availability
        )
        loan_unit_of_work_mock.loans.update.side_effect = lambda entity: entity

        use_case = ReturningLoanUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
            loan_cache_invalidation_outbound=loan_cache_invalidation_outbound_mock,
        )

        response = await use_case.execute(command, authenticated_user)

        updated_entity = loan_unit_of_work_mock.loans.update.await_args.args[0]

        assert isinstance(updated_entity, LoanEntity)
        assert updated_entity.status == LoanStatusEnum.RETURNED
        assert updated_entity.returned_at is not None
        assert response == ReturningLoanResponseDto.response(updated_entity)

        loan_unit_of_work_mock.loans.find_by_id.assert_awaited_once_with(
            command.loan_id
        )
        loan_unit_of_work_mock.book_availability.find_by_id.assert_awaited_once_with(
            loan.book_id
        )
        loan_unit_of_work_mock.book_availability.update_available_copies.assert_awaited_once_with(
            loan.book_id, 3
        )
        loan_unit_of_work_mock.commit.assert_awaited_once()
        loan_cache_invalidation_outbound_mock.invalidate.assert_awaited_once_with(
            authenticated_user.id
        )

    @pytest.mark.asyncio
    async def test_should_return_loan_with_zero_available_copies_when_book_availability_is_not_found(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        loan_cache_invalidation_outbound_mock: AsyncMock,
    ) -> None:
        authenticated_user = _build_authenticated_user(faker)
        loan = _build_active_loan(faker, member_id=authenticated_user.id)
        command = _build_command(faker, loan_id=loan.id)

        loan_unit_of_work_mock.loans.find_by_id.return_value = loan
        loan_unit_of_work_mock.book_availability.find_by_id.return_value = None
        loan_unit_of_work_mock.loans.update.side_effect = lambda entity: entity

        use_case = ReturningLoanUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
            loan_cache_invalidation_outbound=loan_cache_invalidation_outbound_mock,
        )

        await use_case.execute(command, authenticated_user)

        updated_entity = loan_unit_of_work_mock.loans.update.await_args.args[0]

        assert updated_entity.status == LoanStatusEnum.RETURNED
        loan_unit_of_work_mock.book_availability.update_available_copies.assert_not_awaited()
        loan_unit_of_work_mock.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_raise_insufficient_permissions_exception_when_user_is_not_member(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        loan_cache_invalidation_outbound_mock: AsyncMock,
    ) -> None:
        use_case = ReturningLoanUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
            loan_cache_invalidation_outbound=loan_cache_invalidation_outbound_mock,
        )

        command = _build_command(faker)
        authenticated_user = _build_authenticated_user(
            faker, role=UserRoleEnum.LIBRARIAN
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        loan_unit_of_work_mock.loans.find_by_id.assert_not_awaited()
        loan_unit_of_work_mock.loans.update.assert_not_awaited()
        loan_unit_of_work_mock.commit.assert_not_awaited()
        loan_cache_invalidation_outbound_mock.invalidate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_loan_not_found_exception_when_loan_does_not_exist(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        loan_cache_invalidation_outbound_mock: AsyncMock,
    ) -> None:
        loan_unit_of_work_mock.loans.find_by_id.return_value = None

        use_case = ReturningLoanUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
            loan_cache_invalidation_outbound=loan_cache_invalidation_outbound_mock,
        )

        command = _build_command(faker)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(LoanNotFoundException):
            await use_case.execute(command, authenticated_user)

        loan_unit_of_work_mock.loans.update.assert_not_awaited()
        loan_unit_of_work_mock.commit.assert_not_awaited()
        loan_cache_invalidation_outbound_mock.invalidate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_insufficient_permissions_exception_when_loan_does_not_belong_to_user(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        loan_cache_invalidation_outbound_mock: AsyncMock,
    ) -> None:
        authenticated_user = _build_authenticated_user(faker)
        loan = _build_active_loan(faker)  # different member_id
        command = _build_command(faker, loan_id=loan.id)

        loan_unit_of_work_mock.loans.find_by_id.return_value = loan

        use_case = ReturningLoanUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
            loan_cache_invalidation_outbound=loan_cache_invalidation_outbound_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        loan_unit_of_work_mock.loans.update.assert_not_awaited()
        loan_unit_of_work_mock.commit.assert_not_awaited()
        loan_cache_invalidation_outbound_mock.invalidate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_loan_already_returned_exception_when_loan_is_already_returned(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        loan_cache_invalidation_outbound_mock: AsyncMock,
    ) -> None:
        authenticated_user = _build_authenticated_user(faker)
        loan = _build_returned_loan(faker, member_id=authenticated_user.id)
        command = _build_command(faker, loan_id=loan.id)

        loan_unit_of_work_mock.loans.find_by_id.return_value = loan

        use_case = ReturningLoanUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
            loan_cache_invalidation_outbound=loan_cache_invalidation_outbound_mock,
        )

        with pytest.raises(LoanAlreadyReturnedException):
            await use_case.execute(command, authenticated_user)

        loan_unit_of_work_mock.loans.update.assert_not_awaited()
        loan_unit_of_work_mock.commit.assert_not_awaited()
        loan_cache_invalidation_outbound_mock.invalidate.assert_not_awaited()
