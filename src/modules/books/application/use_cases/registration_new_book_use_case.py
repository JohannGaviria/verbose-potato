"""This module contains the registration new book use case."""

from src.modules.books.application.dtos.registration_new_book_dto import (
    RegistrationNewBookCommandDto,
)
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class RegistrationNewBookUseCase:
    """."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
    ) -> None:
        """Initializes the RegistrationNewBookUseCase."""
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def execute(
        self, command: RegistrationNewBookCommandDto
    ) -> None:  # RegistrationNewBookResponseDto:
        """."""
        self._logger.debug("Executing: Registration new book use case.")

        try:
            ...
        except BaseDomainException as exc:
            self._logger.warning(
                "Business rule violated while registering a new book.",
                error=str(exc),
            )
            raise
        finally:
            self._logger.debug("Executed: Registration new book use case.")
