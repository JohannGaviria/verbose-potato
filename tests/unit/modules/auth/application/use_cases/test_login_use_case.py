from unittest.mock import AsyncMock, Mock

import pytest
from faker import Faker

from src.modules.auth.application.dtos.login_dto import (
    LoginCommandDto,
    LoginResponseDto,
)
from src.modules.auth.application.use_cases.login_use_case import LoginUseCase
from src.modules.auth.domain.exceptions.authentication_exception import (
    InvalidCredentialsException,
)
from src.modules.auth.domain.value_objects.access_token_claims_vo import (
    AccessTokenClaimsVO,
)
from src.modules.auth.domain.value_objects.access_token_result_vo import (
    AccessTokenResultVO,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException
from src.shared.domain.value_objects.access_token_vo import AccessTokenVO


def _valid_password(faker: Faker) -> str:
    return faker.password(
        length=16,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )


class TestLoginUseCase:
    @pytest.mark.asyncio
    async def test_should_login_successfully_when_credentials_are_valid(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        password_hash_outbound_mock: Mock,
        token_generator_outbound_mock: Mock,
        user_unit_of_work_mock: AsyncMock,
    ) -> None:
        email = faker.email()
        password = _valid_password(faker)

        exists_user = Mock()
        exists_user.id = faker.uuid4(cast_to=None)
        exists_user.name.value = faker.name()
        exists_user.email.value = email
        exists_user.role = UserRoleEnum.MEMBER
        exists_user.password = Mock()

        user_unit_of_work_mock.users.find_by_email.return_value = exists_user
        password_hash_outbound_mock.verify.return_value = True

        token_result = AccessTokenResultVO(
            access_token=AccessTokenVO(faker.sha256()),
            token_type="Bearer",
            expires_in=3600,
        )
        token_generator_outbound_mock.generate_access.return_value = token_result

        use_case = LoginUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            user_unit_of_work=user_unit_of_work_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_generator_outbound=token_generator_outbound_mock,
        )

        command = LoginCommandDto(email=email, password=password)

        response = await use_case.execute(command)

        user_unit_of_work_mock.users.find_by_email.assert_awaited_once()
        password_hash_outbound_mock.verify.assert_called_once()
        token_generator_outbound_mock.generate_access.assert_called_once()

        verify_args = password_hash_outbound_mock.verify.call_args.args
        assert verify_args[0].value == password
        assert verify_args[1] == exists_user.password

        claims_arg = token_generator_outbound_mock.generate_access.call_args.args[0]
        assert isinstance(claims_arg, AccessTokenClaimsVO)
        assert claims_arg.sub == exists_user.id
        assert claims_arg.role == exists_user.role

        assert response == LoginResponseDto.response(exists_user, token_result)

    @pytest.mark.asyncio
    async def test_should_raise_invalid_credentials_exception_when_user_is_not_found(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        password_hash_outbound_mock: Mock,
        token_generator_outbound_mock: Mock,
        user_unit_of_work_mock: AsyncMock,
    ) -> None:
        user_unit_of_work_mock.users.find_by_email.return_value = None

        use_case = LoginUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            user_unit_of_work=user_unit_of_work_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_generator_outbound=token_generator_outbound_mock,
        )

        command = LoginCommandDto(email=faker.email(), password=_valid_password(faker))

        with pytest.raises(InvalidCredentialsException):
            await use_case.execute(command)

        user_unit_of_work_mock.users.find_by_email.assert_awaited_once()
        password_hash_outbound_mock.verify.assert_not_called()
        token_generator_outbound_mock.generate_access.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_raise_invalid_credentials_exception_when_password_does_not_match(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        password_hash_outbound_mock: Mock,
        token_generator_outbound_mock: Mock,
        user_unit_of_work_mock: AsyncMock,
    ) -> None:
        exists_user = Mock()
        user_unit_of_work_mock.users.find_by_email.return_value = exists_user
        password_hash_outbound_mock.verify.return_value = False

        use_case = LoginUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            user_unit_of_work=user_unit_of_work_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_generator_outbound=token_generator_outbound_mock,
        )

        command = LoginCommandDto(email=faker.email(), password=_valid_password(faker))

        with pytest.raises(InvalidCredentialsException):
            await use_case.execute(command)

        user_unit_of_work_mock.users.find_by_email.assert_awaited_once()
        password_hash_outbound_mock.verify.assert_called_once()
        token_generator_outbound_mock.generate_access.assert_not_called()

    @pytest.mark.parametrize(
        "email",
        [
            "",
            "test",
            "test@",
            "@gmail.com",
            "test.com",
        ],
    )
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_email_is_invalid(
        self,
        faker: Faker,
        email: str,
        logger_factory_outbound_mock: Mock,
        password_hash_outbound_mock: Mock,
        token_generator_outbound_mock: Mock,
        user_unit_of_work_mock: AsyncMock,
    ) -> None:
        use_case = LoginUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            user_unit_of_work=user_unit_of_work_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_generator_outbound=token_generator_outbound_mock,
        )

        command = LoginCommandDto(email=email, password=_valid_password(faker))

        with pytest.raises(BaseDomainException):
            await use_case.execute(command)

        user_unit_of_work_mock.users.find_by_email.assert_not_awaited()
        password_hash_outbound_mock.verify.assert_not_called()
        token_generator_outbound_mock.generate_access.assert_not_called()

    @pytest.mark.parametrize(
        "password",
        [
            "",
            "Aa1!",
            "Aa1!" * 5,
            "password1!",
            "PASSWORD1!",
            "Password!",
            "Password1",
        ],
    )
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_password_is_invalid(
        self,
        faker: Faker,
        password: str,
        logger_factory_outbound_mock: Mock,
        password_hash_outbound_mock: Mock,
        token_generator_outbound_mock: Mock,
        user_unit_of_work_mock: AsyncMock,
    ) -> None:
        use_case = LoginUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            user_unit_of_work=user_unit_of_work_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_generator_outbound=token_generator_outbound_mock,
        )

        command = LoginCommandDto(email=faker.email(), password=password)

        with pytest.raises(BaseDomainException):
            await use_case.execute(command)

        user_unit_of_work_mock.users.find_by_email.assert_not_awaited()
        password_hash_outbound_mock.verify.assert_not_called()
        token_generator_outbound_mock.generate_access.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_propagate_exception_when_user_unit_of_work_raises(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        password_hash_outbound_mock: Mock,
        token_generator_outbound_mock: Mock,
        user_unit_of_work_mock: AsyncMock,
    ) -> None:
        user_unit_of_work_mock.users.find_by_email.side_effect = RuntimeError(
            "unexpected database error"
        )

        use_case = LoginUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            user_unit_of_work=user_unit_of_work_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_generator_outbound=token_generator_outbound_mock,
        )

        command = LoginCommandDto(email=faker.email(), password=_valid_password(faker))

        with pytest.raises(RuntimeError):
            await use_case.execute(command)

        password_hash_outbound_mock.verify.assert_not_called()
        token_generator_outbound_mock.generate_access.assert_not_called()
