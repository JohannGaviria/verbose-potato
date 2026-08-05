"""This module contains the new user registration use case class."""

from src.modules.auth.application.dtos.new_user_registration_dto import (
    NewUserRegistrationCommandDto,
    NewUserRegistrationResponseDto,
)
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.exceptions.user_exception import UserAlreadyExistsException
from src.modules.auth.domain.ports.outbound.password_hash_outbound_port import (
    PasswordHashOutboundPort,
)
from src.modules.auth.domain.ports.unit_of_work.user_unit_of_work_port import (
    UserUnitOfWorkPort,
)
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class NewUserRegistrationUseCase:
    """Creates a new user."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        password_hash_outbound: PasswordHashOutboundPort,
        user_unit_of_work: UserUnitOfWorkPort,
    ) -> None:
        """Initializes the NewUserRegistrationUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
            password_hash_outbound (PasswordHashOutboundPort): Outbound used to hash plain-text passwords.
            user_unit_of_work (UserUnitOfWorkPort): Unit of work used to persist user entities.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self._password_hash_outbound = password_hash_outbound
        self._user_unit_of_work = user_unit_of_work

    async def execute(
        self, command: NewUserRegistrationCommandDto
    ) -> NewUserRegistrationResponseDto:
        """Executes the new user registration use case.

        Validates the provided data, ensures that no user already exists, hashes the password,
        creates the user entity, and persists it.

        Args:
            command (NewUserRegistrationCommandDto): Data required to create the new user.

        Returns:
            NewUserRegistrationResponseDto: The response DTO for the new user registration.

        Raises:
            UserAlreadyExistsException: If a user already exists.
            BaseDomainException: If any domain validation or business rule is violated.
        """
        self._logger.debug(
            "Executing: New user registration use case", email=command.email
        )

        try:
            # Validate value objects immediately upon creation.
            name = NameVO(command.name)
            email = EmailVO(command.email)
            password = PlainPasswordVO(command.password)

            async with self._user_unit_of_work as uow:
                exists_user = await uow.users.find_by_email(email)

                if exists_user:
                    self._logger.warning("User already exists.", email=command.email)
                    raise UserAlreadyExistsException()

                password_hash = self._password_hash_outbound.hash(password)

                entity = UserEntity.create(
                    name=name,
                    email=email,
                    password=password_hash,
                    role=UserRoleEnum.MEMBER,
                )

                user = await uow.users.save(entity)
                await uow.commit()

            self._logger.debug(
                "User created successfully.", user_id=user.id, email=user.email.value
            )

            return NewUserRegistrationResponseDto.response(user)

        except BaseDomainException as exc:
            self._logger.warning(
                "Business rule violated while new user registration.",
                error=str(exc),
                email=command.email,
            )
            raise

        finally:
            self._logger.debug("Executed: New user registration use case.")
