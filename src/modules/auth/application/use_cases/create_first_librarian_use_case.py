"""This module contains the create first librarian use case class."""

from src.modules.auth.application.dtos.create_first_librarian_dto import (
    CreateFirstLibrarianCommandDto,
)
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.exceptions.user_exception import (
    LibrarianAlreadyExistsException,
)
from src.modules.auth.domain.ports.outbound.password_hash_outbound_port import (
    PasswordHashOutboundPort,
)
from src.modules.auth.domain.ports.repositories.user_repository_port import (
    UserRepositoryPort,
)
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.base_exception import BaseException
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class CreateFirstLibrarianUseCase:
    """Creates the initial librarian user if one does not already exist."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        password_hash_outbound: PasswordHashOutboundPort,
        user_repository: UserRepositoryPort,
    ) -> None:
        """Initializes the CreateFirstLibrarianUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
            password_hash_outbound (PasswordHashOutboundPort): Outbound used to hash plain-text passwords.
            user_repository (UserRepositoryPort): Repository used to interact with the user entity.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self._password_hash_outbound = password_hash_outbound
        self._user_repository = user_repository

    async def execute(self, command: CreateFirstLibrarianCommandDto) -> None:
        """Creates the first librarian account.

        Validates the provided data, ensures that no librarian account already
        exists, hashes the password, creates the user entity, and persists it.

        Args:
            command: Data required to create the first librarian account.

        Raises:
            LibrarianAlreadyExistsException: If a librarian account already exists.
            BaseException: If any domain validation or business rule is violated.
        """
        self._logger.debug(
            "Executing: Create first librarian use case.", email=command.email
        )

        try:
            # Validate value objects immediately upon creation.
            name_vo = NameVO(command.name)
            email_vo = EmailVO(command.email)
            plain_password_vo = PlainPasswordVO(command.password)

            if await self._user_repository.exists_librarian():
                self._logger.error("A librarian user is already registered.")
                raise LibrarianAlreadyExistsException()

            password_hash = self._password_hash_outbound.hash(plain_password_vo)

            entity = UserEntity.create(
                name=name_vo,
                email=email_vo,
                password=password_hash,
                role=UserRoleEnum.LIBRARIAN,
            )

            user = await self._user_repository.save(entity)

        except BaseException as exc:
            self._logger.warning(
                "Business rule violated while creating first librarian.",
                error=str(exc),
                email=command.email,
            )
            raise

        self._logger.debug(
            "Librarian created successfully.",
            librarian_id=user.id,
            email=user.email.value,
        )
        self._logger.debug("Executed: Create first librarian use case.")
