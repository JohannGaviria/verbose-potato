"""This module contains the create first librarian runner class."""

from src.modules.auth.application.dtos.create_first_librarian_dto import (
    CreateFirstLibrarianCommandDto,
)
from src.modules.auth.application.use_cases.create_first_librarian_use_case import (
    CreateFirstLibrarianUseCase,
)
from src.modules.auth.domain.exceptions.user_exception import (
    LibrarianAlreadyExistsException,
)
from src.shared.domain.exceptions.base_exception import BaseException
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class CreateFirstLibrarianRunner:
    """Runs the system task responsible for creating the first librarian account."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        create_first_librarian_use_case: CreateFirstLibrarianUseCase,
        data: CreateFirstLibrarianCommandDto,
    ) -> None:
        """Initializes the CreateFirstLibrarianRunner.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
            create_first_librarian_use_case (CreateFirstLibrarianUseCase): Use case used to create the first librarian.
            data (CreateFirstLibrarianCommandDto): Data required to create the first librarian account.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self._use_case = create_first_librarian_use_case
        self._data = data

    async def run(self) -> None:
        """Executes the first librarian creation process.

        This method invokes the corresponding use case using the configured
        bootstrap data. Business exceptions are logged and re-raised, while
        unexpected exceptions are also logged before being propagated.
        """
        self._logger.info("Starting first librarian creation...")

        try:
            await self._use_case.execute(self._data)
            self._logger.info("First librarian created successfully.")
        except LibrarianAlreadyExistsException as exc:
            self._logger.info(
                "First librarian already exists. Skipping bootstrap.",
                error=str(exc),
            )
        except BaseException as exc:
            self._logger.error("Error while creating first librarian.", error=str(exc))
            raise
        except Exception as exc:
            self._logger.error(
                "Unexpected error while creating first librarian.", error=str(exc)
            )
            raise
