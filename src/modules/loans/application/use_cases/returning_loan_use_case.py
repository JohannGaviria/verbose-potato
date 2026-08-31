"""This module contains the returning loan use case."""

from src.modules.loans.application.dtos.returning_loan_dto import (
    ReturningLoanCommandDto,
    ReturningLoanResponseDto,
)
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.exceptions.loan_exception import (
    LoanAlreadyReturnedException,
    LoanNotFoundException,
)
from src.modules.loans.domain.ports.outbound.loan_cache_invalidation_outbound_port import (
    LoanCacheInvalidationOutboundPort,
)
from src.modules.loans.domain.ports.unit_of_work.loan_unit_of_work_port import (
    LoanUnitOfWorkPort,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.services.authorization_service import AuthorizationService


class ReturningLoanUseCase:
    """Return loan use case."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        loan_unit_of_work: LoanUnitOfWorkPort,
        loan_cache_invalidation_outbound: LoanCacheInvalidationOutboundPort,
    ) -> None:
        """Initializes the ReturningLoanUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
            loan_unit_of_work (LoanUnitOfWorkPort): Unit of work used to persist loan entities and book
                operations cross-module.
            loan_cache_invalidation_outbound (LoanCacheInvalidationOutboundPort): Outbound used to invalidate
                the loan catalog, member loan, and book catalog caches.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self._loan_unit_of_work = loan_unit_of_work
        self._loan_cache_invalidation_outbound = loan_cache_invalidation_outbound
        self._authorization_service = AuthorizationService()

    async def execute(
        self,
        command: ReturningLoanCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> ReturningLoanResponseDto:
        """Execute the returning loan use case.

        Args:
            command (ReturningLoanCommandDto): Data required to execute the returning loan use case.
            authenticated_user (AuthenticatedUserCommandDto): Data required to authenticate the user.

        Returns:
            ReturningLoanResponseDto: The response DTO for the returning loan.

        Raises:
            LoanNotFoundException: Raised when the loan cannot be found.
            InsufficientPermissionsException: Raised when the user is not the owner of the loan.
            LoanAlreadyReturnedException: Raised when the loan has already been returned.
        """
        self._logger.debug("Executing: returning loan use case.")

        try:
            self._authorization_service.assert_role(
                authenticated_user.role, UserRoleEnum.MEMBER
            )

            async with self._loan_unit_of_work as uow:
                loan = await uow.loans.find_by_id(command.loan_id)

                if loan is None:
                    self._logger.error("Loan does not exist.", loan_id=command.loan_id)
                    raise LoanNotFoundException()

                self._authorization_service.assert_ownership(
                    resource_owner_id=loan.member_id,
                    user_id=authenticated_user.id,
                )

                if loan.status == LoanStatusEnum.RETURNED:
                    self._logger.error(
                        "Loan has already been returned.",
                        loan_id=command.loan_id,
                    )
                    raise LoanAlreadyReturnedException(command.loan_id)

                book_availability = await uow.book_availability.find_by_id(loan.book_id)

                if book_availability is not None:
                    available_copies = book_availability.increase_available_copies()
                    await uow.book_availability.update_available_copies(
                        loan.book_id, available_copies
                    )

                returned_loan = loan.mark_returned()
                updated_loan = await uow.loans.update(returned_loan)
                await uow.commit()

            await self._loan_cache_invalidation_outbound.invalidate(
                authenticated_user.id
            )

            self._logger.debug(
                "Loan successfully returned.",
                loan_id=updated_loan.id,
                member_id=authenticated_user.id,
                book_id=updated_loan.book_id,
            )

            return ReturningLoanResponseDto.response(updated_loan)

        except BaseDomainException as exc:
            self._logger.warning(
                "Business rule violated while returning loan.",
                error=str(exc),
            )
            raise
        finally:
            self._logger.debug("Executed: returning loan use case.")
