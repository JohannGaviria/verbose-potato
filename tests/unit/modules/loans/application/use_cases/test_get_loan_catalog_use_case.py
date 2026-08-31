from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from faker import Faker

from src.modules.loans.application.dtos.get_loan_catalog_dto import (
    GetLoanCatalogCommandDto,
    GetLoanCatalogResponseDto,
)
from src.modules.loans.application.use_cases.get_loan_catalog_use_case import (
    GetLoanCatalogUseCase,
)
from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.exceptions.loan_exception import (
    InvalidLoanCatalogQueryException,
)
from src.modules.loans.domain.value_objects.loan_catalog_cache_key_vo import (
    LoanCatalogCacheKeyVO,
)
from src.modules.loans.domain.value_objects.loan_catalog_cache_value_vo import (
    LoanCatalogCacheValueVO,
)
from src.modules.loans.domain.value_objects.loan_catalog_query_vo import (
    LoanCatalogQueryVO,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.authentication_authorization_exception import (
    InsufficientPermissionsException,
)
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO

_CACHE_TTL_SECONDS = 600


def _build_active_loan(faker: Faker) -> LoanEntity:
    now = datetime.now(UTC)
    return LoanEntity(
        id=faker.uuid4(cast_to=None),
        member_id=faker.uuid4(cast_to=None),
        book_id=faker.uuid4(cast_to=None),
        status=LoanStatusEnum.ACTIVE,
        loaned_at=now,
        returned_at=None,
        created_at=now,
        updated_at=now,
    )


def _build_command(
    member_id: Any = None,
    book_id: Any = None,
    status: LoanStatusEnum | None = None,
    sort_by: Any = None,
    sort_order: Any = None,
    page: int = 1,
    page_size: int = 20,
) -> GetLoanCatalogCommandDto:
    return GetLoanCatalogCommandDto(
        member_id=member_id,
        book_id=book_id,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


def _build_authenticated_user(
    faker: Faker, role: UserRoleEnum = UserRoleEnum.LIBRARIAN
) -> AuthenticatedUserCommandDto:
    return AuthenticatedUserCommandDto(id=faker.uuid4(cast_to=None), role=role)


class TestGetLoanCatalogUseCase:
    @pytest.mark.asyncio
    async def test_should_return_loans_from_database_when_cache_miss(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        cache_outbound_mock.get.return_value = None
        authenticated_user = _build_authenticated_user(faker)
        loans = [_build_active_loan(faker), _build_active_loan(faker)]
        loan_unit_of_work_mock.loans.find_catalog.return_value = (loans, 2)

        use_case = GetLoanCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
        )

        command = _build_command(page=1, page_size=20)
        response = await use_case.execute(command, authenticated_user)

        expected_query = LoanCatalogQueryVO(
            member_id=None,
            book_id=None,
            status=None,
            sort_by=None,
            sort_order=None,
            page=1,
            page_size=20,
        )
        expected_key = LoanCatalogCacheKeyVO.from_filters(expected_query)
        expected_response = GetLoanCatalogResponseDto.response(
            loans=loans, total=2, page=1, page_size=20
        )

        assert response == expected_response

        cache_outbound_mock.get.assert_awaited_once_with(expected_key)
        loan_unit_of_work_mock.loans.find_catalog.assert_awaited_once_with(
            expected_query
        )

        cache_outbound_mock.set.assert_awaited_once()
        entry = cache_outbound_mock.set.await_args.args[0]

        assert isinstance(entry, CacheEntryVO)
        assert entry.key == expected_key
        assert entry.ttl == CacheTTLVO(seconds=_CACHE_TTL_SECONDS)
        assert entry.value == expected_response.to_cache_value()

        logger = logger_factory_outbound_mock.get_logger.return_value
        logger.debug.assert_any_call(
            "Cache MISS while retrieving the loan catalog.",
            cache_key=expected_key.value(),
        )
        logger.debug.assert_any_call("Loan catalog successfully retrieved.")

    @pytest.mark.asyncio
    async def test_should_return_loans_from_cache_when_cache_hit(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        authenticated_user = _build_authenticated_user(faker)
        now = datetime.now(UTC)
        cached_value = LoanCatalogCacheValueVO(
            items=(
                {
                    "id": str(faker.uuid4(cast_to=None)),
                    "member_id": str(faker.uuid4(cast_to=None)),
                    "book_id": str(faker.uuid4(cast_to=None)),
                    "status": "ACTIVE",
                    "loaned_at": now.isoformat(),
                    "returned_at": None,
                    "created_at": now.isoformat(),
                    "updated_at": now.isoformat(),
                },
            ),
            total=1,
            page=1,
            page_size=20,
            total_pages=1,
        )
        cache_outbound_mock.get.return_value = cached_value

        use_case = GetLoanCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
        )

        command = _build_command()
        response = await use_case.execute(command, authenticated_user)

        expected_query = LoanCatalogQueryVO(
            member_id=None,
            book_id=None,
            status=None,
            sort_by=None,
            sort_order=None,
            page=1,
            page_size=20,
        )
        expected_key = LoanCatalogCacheKeyVO.from_filters(expected_query)

        assert response == GetLoanCatalogResponseDto.from_cache_value(cached_value)

        cache_outbound_mock.get.assert_awaited_once_with(expected_key)
        loan_unit_of_work_mock.loans.find_catalog.assert_not_awaited()
        cache_outbound_mock.set.assert_not_awaited()

        logger = logger_factory_outbound_mock.get_logger.return_value
        logger.debug.assert_any_call(
            "Cache HIT while retrieving the loan catalog.",
            cache_key=expected_key.value(),
        )

    @pytest.mark.asyncio
    async def test_should_build_query_with_provided_filters_and_sorting(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        cache_outbound_mock.get.return_value = None
        loan_unit_of_work_mock.loans.find_catalog.return_value = ([], 0)
        authenticated_user = _build_authenticated_user(faker)
        member_id = uuid4()
        book_id = uuid4()

        use_case = GetLoanCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
        )

        command = _build_command(
            member_id=member_id,
            book_id=book_id,
            status=LoanStatusEnum.RETURNED,
            sort_by=LoanSortByEnum.RETURNED_AT,
            sort_order=SortOrderEnum.DESC,
            page=2,
            page_size=10,
        )

        await use_case.execute(command, authenticated_user)

        expected_query = LoanCatalogQueryVO(
            member_id=member_id,
            book_id=book_id,
            status=LoanStatusEnum.RETURNED,
            sort_by=LoanSortByEnum.RETURNED_AT,
            sort_order=SortOrderEnum.DESC,
            page=2,
            page_size=10,
        )

        loan_unit_of_work_mock.loans.find_catalog.assert_awaited_once_with(
            expected_query
        )
        cache_outbound_mock.get.assert_awaited_once_with(
            LoanCatalogCacheKeyVO.from_filters(expected_query)
        )

    @pytest.mark.asyncio
    async def test_should_raise_insufficient_permissions_exception_when_user_is_not_librarian(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetLoanCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
        )

        command = _build_command()
        authenticated_user = _build_authenticated_user(faker, role=UserRoleEnum.MEMBER)

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        cache_outbound_mock.get.assert_not_awaited()
        cache_outbound_mock.set.assert_not_awaited()
        loan_unit_of_work_mock.loans.find_catalog.assert_not_awaited()

    @pytest.mark.parametrize("status", ["PENDING", "UNKNOWN", 1])
    @pytest.mark.asyncio
    async def test_should_raise_value_error_when_status_is_not_a_valid_option(
        self,
        faker: Faker,
        status: Any,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetLoanCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
        )

        command = _build_command(status=status)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(ValueError):
            await use_case.execute(command, authenticated_user)

        cache_outbound_mock.get.assert_not_awaited()
        loan_unit_of_work_mock.loans.find_catalog.assert_not_awaited()

    @pytest.mark.parametrize("sort_by", ["invalid_field", "name"])
    @pytest.mark.asyncio
    async def test_should_raise_value_error_when_sort_by_is_not_a_valid_option(
        self,
        faker: Faker,
        sort_by: str,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetLoanCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
        )

        command = _build_command(sort_by=sort_by)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(ValueError):
            await use_case.execute(command, authenticated_user)

        cache_outbound_mock.get.assert_not_awaited()
        loan_unit_of_work_mock.loans.find_catalog.assert_not_awaited()

    @pytest.mark.parametrize("sort_order", ["ascending", "descending"])
    @pytest.mark.asyncio
    async def test_should_raise_value_error_when_sort_order_is_not_a_valid_option(
        self,
        faker: Faker,
        sort_order: str,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetLoanCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
        )

        command = _build_command(sort_order=sort_order)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(ValueError):
            await use_case.execute(command, authenticated_user)

        cache_outbound_mock.get.assert_not_awaited()
        loan_unit_of_work_mock.loans.find_catalog.assert_not_awaited()

    @pytest.mark.parametrize("page", [0, -1, True])
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_page_is_invalid(
        self,
        faker: Faker,
        page: Any,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetLoanCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
        )

        command = _build_command(page=page)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(InvalidLoanCatalogQueryException):
            await use_case.execute(command, authenticated_user)

        cache_outbound_mock.get.assert_not_awaited()
        loan_unit_of_work_mock.loans.find_catalog.assert_not_awaited()

    @pytest.mark.parametrize("page_size", [0, -1, True, 101])
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_page_size_is_invalid(
        self,
        faker: Faker,
        page_size: Any,
        logger_factory_outbound_mock: Mock,
        loan_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetLoanCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            loan_unit_of_work=loan_unit_of_work_mock,
        )

        command = _build_command(page_size=page_size)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(InvalidLoanCatalogQueryException):
            await use_case.execute(command, authenticated_user)

        cache_outbound_mock.get.assert_not_awaited()
        loan_unit_of_work_mock.loans.find_catalog.assert_not_awaited()
