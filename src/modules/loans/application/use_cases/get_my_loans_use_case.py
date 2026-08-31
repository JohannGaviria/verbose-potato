"""This module contains the get my loans use case."""

from src.modules.loans.application.dtos.get_my_loans_dto import (
    GetMyLoansCommandDto,
    GetMyLoansResponseDto,
)
from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.ports.unit_of_work.loan_unit_of_work_port import (
    LoanUnitOfWorkPort,
)
from src.modules.loans.domain.value_objects.member_loan_cache_key_vo import (
    MemberLoanCacheKeyVO,
)
from src.modules.loans.domain.value_objects.member_loan_cache_value_vo import (
    MemberLoanCacheValueVO,
)
from src.modules.loans.domain.value_objects.member_loan_query_vo import (
    MemberLoanQueryVO,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException
from src.shared.domain.ports.outbound.cache_outbound_port import CacheOutboundPort
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.services.authorization_service import AuthorizationService
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO

_MEMBER_LOAN_CACHE_TTL_SECONDS = 600  # 10 Minutes


class GetMyLoansUseCase:
    """Get the paginated loans of the authenticated member use case."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        cache_outbound: CacheOutboundPort[MemberLoanCacheValueVO],
        loan_unit_of_work: LoanUnitOfWorkPort,
    ) -> None:
        """Initializes the GetMyLoansUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
            cache_outbound (CacheOutboundPort[MemberLoanCacheValueVO]): Cache outbound used to read and store
                the member loans.
            loan_unit_of_work (LoanUnitOfWorkPort): Unit of work used to retrieve the member loans.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self._cache_outbound = cache_outbound
        self._loan_unit_of_work = loan_unit_of_work
        self._authorization_service = AuthorizationService()

    async def execute(
        self,
        command: GetMyLoansCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> GetMyLoansResponseDto:
        """Execute the get my loans use case.

        Args:
            command (GetMyLoansCommandDto): Data required to execute the get my loans use case.
            authenticated_user (AuthenticatedUserCommandDto): Data required to authenticate the user.

        Returns:
            GetMyLoansResponseDto: The response DTO for the get my loans.

        Raises:
            InsufficientPermissionsException: Raised when the user is not a member.
        """
        self._logger.debug("Executing: get my loans use case.")

        try:
            self._authorization_service.assert_role(
                authenticated_user.role, UserRoleEnum.MEMBER
            )

            status = LoanStatusEnum(command.status) if command.status else None
            sort_by = LoanSortByEnum(command.sort_by) if command.sort_by else None
            sort_order = (
                SortOrderEnum(command.sort_order) if command.sort_order else None
            )

            query = MemberLoanQueryVO(
                status=status,
                sort_by=sort_by,
                sort_order=sort_order,
                page=command.page,
                page_size=command.page_size,
            )
            cache_key = MemberLoanCacheKeyVO.from_filters(authenticated_user.id, query)
            cached_value = await self._cache_outbound.get(cache_key)

            if cached_value is not None:
                self._logger.debug(
                    "Cache HIT while retrieving the member loans.",
                    cache_key=cache_key.value(),
                )
                return GetMyLoansResponseDto.from_cache_value(cached_value)

            self._logger.debug(
                "Cache MISS while retrieving the member loans.",
                cache_key=cache_key.value(),
            )

            async with self._loan_unit_of_work as uow:
                loans, total = await uow.loans.find_by_member(
                    authenticated_user.id, query
                )

            response = GetMyLoansResponseDto.response(
                loans=loans,
                total=total,
                page=query.page,
                page_size=query.page_size,
            )

            entry = CacheEntryVO(
                key=cache_key,
                ttl=CacheTTLVO(seconds=_MEMBER_LOAN_CACHE_TTL_SECONDS),
                value=response.to_cache_value(),
            )
            await self._cache_outbound.set(entry)

            self._logger.debug(
                "Member loans successfully retrieved.",
                member_id=authenticated_user.id,
            )

            return response

        except BaseDomainException as exc:
            self._logger.warning(
                "Business rule violated while get my loans.",
                error=str(exc),
            )
            raise
        finally:
            self._logger.debug("Executed: get my loans use case.")
