"""This module contains the login use case."""

from src.modules.auth.application.dtos.login_dto import (
    LoginCommandDto,
    LoginResponseDto,
)
from src.modules.auth.domain.exceptions.authentication_exception import (
    InvalidCredentialsException,
)
from src.modules.auth.domain.ports.outbound.password_hash_outbound_port import (
    PasswordHashOutboundPort,
)
from src.modules.auth.domain.ports.outbound.token_generator_outbound_port import (
    TokenGeneratorOutboundPort,
)
from src.modules.auth.domain.ports.unit_of_work.user_unit_of_work_port import (
    UserUnitOfWorkPort,
)
from src.modules.auth.domain.value_objects.access_token_claims_vo import (
    AccessTokenClaimsVO,
)
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class LoginUseCase:
    """Login a user."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        user_unit_of_work: UserUnitOfWorkPort,
        password_hash_outbound: PasswordHashOutboundPort,
        token_generator_outbound: TokenGeneratorOutboundPort,
    ) -> None:
        """Initializes the LoginUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to created the logger instance.
            user_unit_of_work (UserUnitOfWorkPort): Unit of work used to persist user entities.
            password_hash_outbound (PasswordHashOutboundPort): Outbound used to hash plain-text passwords.
            token_generator_outbound (TokenGeneratorOutboundPort): Outbound used to generate tokens.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self._user_unit_of_work = user_unit_of_work
        self._password_hash_outbound = password_hash_outbound
        self._token_generator_outbound = token_generator_outbound

    async def execute(self, command: LoginCommandDto) -> LoginResponseDto:
        """Login a user.

        Validates the provided data, ensures that no user account already

        Args:
            command (LoginCommandDto): Data required to login.

        Returns:
            LoginResponseDto: The response DTO for the login.

        Raises:
            InvalidCredentialsException: If the provided credentials are invalid.
        """
        self._logger.debug("Executing: Login use case.", email=command.email)

        try:
            # Validate value objects immediately upon creation.
            email = EmailVO(command.email)
            password = PlainPasswordVO(command.password)

            async with self._user_unit_of_work as uow:
                exists_user = await uow.users.find_by_email(email)
                if not exists_user:
                    self._logger.error("User not found.", email=command.email)
                    raise InvalidCredentialsException()

                if not self._password_hash_outbound.verify(
                    password, exists_user.password
                ):
                    self._logger.error("Invalid password.", email=command.email)
                    raise InvalidCredentialsException()

                claims = AccessTokenClaimsVO.create(exists_user.id, exists_user.role)
                access_token = self._token_generator_outbound.generate_access(claims)

            self._logger.debug("Login successful.", email=command.email)

            return LoginResponseDto.response(exists_user, access_token)

        except BaseDomainException as exc:
            self._logger.warning(
                "Business rule violated while logging in.",
                error=str(exc),
                email=command.email,
            )
            raise

        finally:
            self._logger.debug("Executed: Login use case.")
