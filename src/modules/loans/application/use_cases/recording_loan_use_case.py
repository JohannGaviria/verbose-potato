"""This module contains the recording loan use case."""

from src.modules.loans.application.dtos.recording_loan_dto import (
    RecordingLoanCommandDto,
    RecordingLoanResponseDto,
)
from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.exceptions.book_reference_exception import (
    BookNotFoundException,
)
from src.modules.loans.domain.exceptions.loan_exception import (
    MemberAlreadyHasActiveLoanException,
)
from src.modules.loans.domain.ports.outbound.loan_cache_invalidation_outbound_port import (
    LoanCacheInvalidationOutboundPort,
)
from src.modules.loans.domain.ports.unit_of_work.loan_unit_of_work_port import (
    LoanUnitOfWorkPort,
)
from src.modules.loans.domain.services.loan_policy_service import LoanPolicyService
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.services.authorization_service import AuthorizationService


class RecordingLoanUseCase:
    """Record loan use case."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        loan_unit_of_work: LoanUnitOfWorkPort,
        loan_cache_invalidation_outbound: LoanCacheInvalidationOutboundPort,
    ) -> None:
        """Initializes the RecordingLoanUseCase.

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
        self._loan_policy_service = LoanPolicyService()

    async def execute(
        self,
        command: RecordingLoanCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> RecordingLoanResponseDto:
        """Execute the recording loan use case.

        Args:
            command (RecordingLoanCommandDto): Data required to execute the recording loan use case.
            authenticated_user (AuthenticatedUserCommandDto): Data required to authenticate the user.

        Returns:
            RecordingLoanResponseDto: The response DTO for the recording loan.

        Raises:
            BookNotFoundException: Raised when the book cannot be found.
        """
        self._logger.debug("Executing: recording loan use case.")

        try:
            self._authorization_service.assert_role(
                authenticated_user.role, UserRoleEnum.MEMBER
            )

            async with self._loan_unit_of_work as uow:
                exists_book = await uow.book_availability.find_by_id(command.book_id)

                if exists_book is None:
                    self._logger.error("Book does not exist.", book_id=command.book_id)
                    raise BookNotFoundException()

                exists_book.ensure_has_available_copies()

                if await uow.loans.exists_active_by_member_and_book(
                    authenticated_user.id, command.book_id
                ):
                    self._logger.error(
                        "Member already has an active loan for the requested book.",
                        member_id=authenticated_user.id,
                        book_id=command.book_id,
                    )
                    raise MemberAlreadyHasActiveLoanException(
                        authenticated_user.id, command.book_id
                    )

                active_loans = await uow.loans.count_active_by_member(
                    authenticated_user.id
                )
                self._loan_policy_service.ensure_member_can_register_loan(active_loans)

                available_copies = exists_book.reduce_available_copies()
                await uow.book_availability.update_available_copies(
                    command.book_id, available_copies
                )

                entity = LoanEntity.create(authenticated_user.id, exists_book.book_id)
                loan = await uow.loans.save(entity)
                await uow.commit()

            await self._loan_cache_invalidation_outbound.invalidate(
                authenticated_user.id
            )

            self._logger.debug(
                "Loan successfully registered.",
                loan_id=loan.id,
                member_id=authenticated_user.id,
                book_id=command.book_id,
            )

            return RecordingLoanResponseDto.response(loan)

        except BaseDomainException as exc:
            self._logger.warning(
                "Business rule violated while recording loan.",
                error=str(exc),
            )
            raise
        finally:
            self._logger.debug("Executed: recording loan use case.")
