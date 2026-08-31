from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.loans.application.dtos.recording_loan_dto import (
    RecordingLoanCommandDto,
    RecordingLoanResponseDto,
)
from src.modules.loans.application.use_cases.recording_loan_use_case import (
    RecordingLoanUseCase,
)
from src.modules.loans.domain.constants.loan_constant import MAX_ACTIVE_LOANS_PER_MEMBER
from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.exceptions.book_reference_exception import (
    BookNotAvailableException,
    BookNotFoundException,
)
from src.modules.loans.domain.exceptions.loan_exception import (
    MaximumActiveLoansExceededException,
    MemberAlreadyHasActiveLoanException,
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
    faker: Faker, book_id: UUID | None = None
) -> RecordingLoanCommandDto:
    return RecordingLoanCommandDto(book_id=book_id or faker.uuid4(cast_to=None))


def _build_authenticated_user(
    faker: Faker, role: UserRoleEnum = UserRoleEnum.MEMBER
) -> AuthenticatedUserCommandDto:
    return AuthenticatedUserCommandDto(id=faker.uuid4(cast_to=None), role=role)


def _build_book_availability(
    book_id: UUID, available_copies: int = 3
) -> BookAvailabilityReferenceVO:
    return BookAvailabilityReferenceVO(
        book_id=book_id, available_copies=available_copies
    )


class TestRecordingLoanUseCase:
    @pytest.mark.asyncio
    async def test_should_register_loan_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        loan_cache_invalidation_outbound_mock: AsyncMock,
    ) -> None:
        command = _build_command(faker)
        authenticated_user = _build_authenticated_user(faker)
        book_availability = _build_book_availability(
            command.book_id, available_copies=3
        )

        loan_unit_of_work_mock.book_availability.find_by_id.return_value = (
            book_availability
        )
        loan_unit_of_work_mock.loans.exists_active_by_member_and_book.return_value = (
            False
        )
        loan_unit_of_work_mock.loans.count_active_by_member.return_value = 0
        loan_unit_of_work_mock.loans.save.side_effect = lambda entity: entity

        use_case = RecordingLoanUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
            loan_cache_invalidation_outbound=loan_cache_invalidation_outbound_mock,
        )

        response = await use_case.execute(command, authenticated_user)

        saved_entity = loan_unit_of_work_mock.loans.save.await_args.args[0]

        assert isinstance(saved_entity, LoanEntity)
        assert saved_entity.member_id == authenticated_user.id
        assert saved_entity.book_id == command.book_id
        assert response == RecordingLoanResponseDto.response(saved_entity)

        loan_unit_of_work_mock.book_availability.find_by_id.assert_awaited_once_with(
            command.book_id
        )
        loan_unit_of_work_mock.loans.exists_active_by_member_and_book.assert_awaited_once_with(
            authenticated_user.id, command.book_id
        )
        loan_unit_of_work_mock.loans.count_active_by_member.assert_awaited_once_with(
            authenticated_user.id
        )
        loan_unit_of_work_mock.book_availability.update_available_copies.assert_awaited_once_with(
            command.book_id, 2
        )
        loan_unit_of_work_mock.commit.assert_awaited_once()
        loan_cache_invalidation_outbound_mock.invalidate.assert_awaited_once_with(
            authenticated_user.id
        )

    @pytest.mark.asyncio
    async def test_should_raise_insufficient_permissions_exception_when_user_is_not_member(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        loan_cache_invalidation_outbound_mock: AsyncMock,
    ) -> None:
        use_case = RecordingLoanUseCase(
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

        loan_unit_of_work_mock.book_availability.find_by_id.assert_not_awaited()
        loan_unit_of_work_mock.loans.save.assert_not_awaited()
        loan_unit_of_work_mock.commit.assert_not_awaited()
        loan_cache_invalidation_outbound_mock.invalidate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_book_not_found_exception_when_book_does_not_exist(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        loan_cache_invalidation_outbound_mock: AsyncMock,
    ) -> None:
        loan_unit_of_work_mock.book_availability.find_by_id.return_value = None

        use_case = RecordingLoanUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
            loan_cache_invalidation_outbound=loan_cache_invalidation_outbound_mock,
        )

        command = _build_command(faker)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(BookNotFoundException):
            await use_case.execute(command, authenticated_user)

        loan_unit_of_work_mock.loans.exists_active_by_member_and_book.assert_not_awaited()
        loan_unit_of_work_mock.loans.save.assert_not_awaited()
        loan_unit_of_work_mock.commit.assert_not_awaited()
        loan_cache_invalidation_outbound_mock.invalidate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_book_not_available_exception_when_book_has_no_available_copies(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        loan_cache_invalidation_outbound_mock: AsyncMock,
    ) -> None:
        command = _build_command(faker)
        book_availability = _build_book_availability(
            command.book_id, available_copies=0
        )
        loan_unit_of_work_mock.book_availability.find_by_id.return_value = (
            book_availability
        )

        use_case = RecordingLoanUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
            loan_cache_invalidation_outbound=loan_cache_invalidation_outbound_mock,
        )

        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(BookNotAvailableException):
            await use_case.execute(command, authenticated_user)

        loan_unit_of_work_mock.loans.exists_active_by_member_and_book.assert_not_awaited()
        loan_unit_of_work_mock.loans.save.assert_not_awaited()
        loan_unit_of_work_mock.commit.assert_not_awaited()
        loan_cache_invalidation_outbound_mock.invalidate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_member_already_has_active_loan_exception_when_member_already_has_an_active_loan_for_the_book(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        loan_cache_invalidation_outbound_mock: AsyncMock,
    ) -> None:
        command = _build_command(faker)
        book_availability = _build_book_availability(
            command.book_id, available_copies=3
        )
        loan_unit_of_work_mock.book_availability.find_by_id.return_value = (
            book_availability
        )
        loan_unit_of_work_mock.loans.exists_active_by_member_and_book.return_value = (
            True
        )

        use_case = RecordingLoanUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
            loan_cache_invalidation_outbound=loan_cache_invalidation_outbound_mock,
        )

        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(MemberAlreadyHasActiveLoanException):
            await use_case.execute(command, authenticated_user)

        loan_unit_of_work_mock.loans.count_active_by_member.assert_not_awaited()
        loan_unit_of_work_mock.loans.save.assert_not_awaited()
        loan_unit_of_work_mock.commit.assert_not_awaited()
        loan_cache_invalidation_outbound_mock.invalidate.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_maximum_active_loans_exceeded_exception_when_member_reached_the_active_loan_limit(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        loan_cache_invalidation_outbound_mock: AsyncMock,
    ) -> None:
        command = _build_command(faker)
        book_availability = _build_book_availability(
            command.book_id, available_copies=3
        )
        loan_unit_of_work_mock.book_availability.find_by_id.return_value = (
            book_availability
        )
        loan_unit_of_work_mock.loans.exists_active_by_member_and_book.return_value = (
            False
        )
        loan_unit_of_work_mock.loans.count_active_by_member.return_value = (
            MAX_ACTIVE_LOANS_PER_MEMBER
        )

        use_case = RecordingLoanUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
            loan_cache_invalidation_outbound=loan_cache_invalidation_outbound_mock,
        )

        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(MaximumActiveLoansExceededException):
            await use_case.execute(command, authenticated_user)

        loan_unit_of_work_mock.book_availability.update_available_copies.assert_not_awaited()
        loan_unit_of_work_mock.loans.save.assert_not_awaited()
        loan_unit_of_work_mock.commit.assert_not_awaited()
        loan_cache_invalidation_outbound_mock.invalidate.assert_not_awaited()
