"""This module contains the get loan catalog use case."""

from src.modules.loans.application.dtos.get_loan_catalog_dto import (
    GetLoanCatalogCommandDto,
    GetLoanCatalogResponseDto,
)
from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.ports.unit_of_work.loan_unit_of_work_port import (
    LoanUnitOfWorkPort,
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
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException
from src.shared.domain.ports.outbound.cache_outbound_port import CacheOutboundPort
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.services.authorization_service import AuthorizationService
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO

_LOAN_CATALOG_CACHE_TTL_SECONDS = 600  # 10 Minutes


class GetLoanCatalogUseCase:
    """Get the paginated loan catalog use case."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        cache_outbound: CacheOutboundPort[LoanCatalogCacheValueVO],
        loan_unit_of_work: LoanUnitOfWorkPort,
    ) -> None:
        """Initializes the GetLoanCatalogUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
            cache_outbound (CacheOutboundPort[LoanCatalogCacheValueVO]): Cache outbound used to read and store
                the loan catalog.
            loan_unit_of_work (LoanUnitOfWorkPort): Unit of work used to retrieve the loan catalog.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self._cache_outbound = cache_outbound
        self._loan_unit_of_work = loan_unit_of_work
        self._authorization_service = AuthorizationService()

    async def execute(
        self,
        command: GetLoanCatalogCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> GetLoanCatalogResponseDto:
        """Execute the get loan catalog use case.

        Args:
            command (GetLoanCatalogCommandDto): Data required to execute the get loan catalog use case.
            authenticated_user (AuthenticatedUserCommandDto): Data required to authenticate the user.

        Returns:
            GetLoanCatalogResponseDto: The response DTO for the get loan catalog use case.

        Raises:
            InsufficientPermissionsException: Raised when the user is not a librarian.
        """
        self._logger.debug("Executing: get loan catalog use case.")

        try:
            self._authorization_service.assert_role(
                authenticated_user.role, UserRoleEnum.LIBRARIAN
            )

            status = LoanStatusEnum(command.status) if command.status else None
            sort_by = LoanSortByEnum(command.sort_by) if command.sort_by else None
            sort_order = (
                SortOrderEnum(command.sort_order) if command.sort_order else None
            )

            query = LoanCatalogQueryVO(
                member_id=command.member_id,
                book_id=command.book_id,
                status=status,
                sort_by=sort_by,
                sort_order=sort_order,
                page=command.page,
                page_size=command.page_size,
            )
            cache_key = LoanCatalogCacheKeyVO.from_filters(query)
            cached_value = await self._cache_outbound.get(cache_key)

            if cached_value is not None:
                self._logger.debug(
                    "Cache HIT while retrieving the loan catalog.",
                    cache_key=cache_key.value(),
                )
                return GetLoanCatalogResponseDto.from_cache_value(cached_value)

            self._logger.debug(
                "Cache MISS while retrieving the loan catalog.",
                cache_key=cache_key.value(),
            )

            async with self._loan_unit_of_work as uow:
                loans, total = await uow.loans.find_catalog(query)

            response = GetLoanCatalogResponseDto.response(
                loans=loans,
                total=total,
                page=query.page,
                page_size=query.page_size,
            )

            entry = CacheEntryVO(
                key=cache_key,
                ttl=CacheTTLVO(seconds=_LOAN_CATALOG_CACHE_TTL_SECONDS),
                value=response.to_cache_value(),
            )
            await self._cache_outbound.set(entry)

            self._logger.debug("Loan catalog successfully retrieved.")

            return response

        except BaseDomainException as exc:
            self._logger.warning(
                "Business rule violated while get loan catalog.",
                error=str(exc),
            )
            raise
        finally:
            self._logger.debug("Executed: get loan catalog use case.")
