from unittest.mock import AsyncMock, Mock

import pytest
from faker import Faker

from src.modules.auth.application.dtos.new_user_registration_dto import (
    NewUserRegistrationCommandDto,
    NewUserRegistrationResponseDto,
)
from src.modules.auth.application.use_cases.new_user_registration_use_case import (
    NewUserRegistrationUseCase,
)
from src.modules.auth.domain.exceptions.user_exception import (
    UserAlreadyExistsException,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException


class TestNewUserRegistrationUseCase:
    @pytest.mark.asyncio
    async def test_should_create_user_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        password_hash_outbound_mock: Mock,
        user_unit_of_work_mock: AsyncMock,
    ) -> None:

        name = faker.name()
        email = faker.email()
        password = faker.password(
            length=16,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        )

        user_unit_of_work_mock.users.find_by_email.return_value = None
        password_hash_outbound_mock.hash.return_value = "hashed-password"

        saved_user = Mock()
        saved_user.id = faker.uuid4()
        saved_user.name.value = name
        saved_user.email.value = email

        user_unit_of_work_mock.users.save.return_value = saved_user

        use_case = NewUserRegistrationUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            password_hash_outbound=password_hash_outbound_mock,
            user_unit_of_work=user_unit_of_work_mock,
        )

        command = NewUserRegistrationCommandDto(
            name=name,
            email=email,
            password=password,
        )

        response = await use_case.execute(command)

        saved_entity = user_unit_of_work_mock.users.save.await_args.args[0]

        assert saved_entity.name.value == name
        assert saved_entity.email.value == email
        assert saved_entity.password == "hashed-password"
        assert saved_entity.role == UserRoleEnum.MEMBER

        assert response == NewUserRegistrationResponseDto.response(saved_user)

        user_unit_of_work_mock.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_raise_user_already_exists_exception_when_email_is_registered(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        password_hash_outbound_mock: Mock,
        user_unit_of_work_mock: AsyncMock,
    ) -> None:

        user_unit_of_work_mock.users.find_by_email.return_value = Mock()

        use_case = NewUserRegistrationUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            password_hash_outbound=password_hash_outbound_mock,
            user_unit_of_work=user_unit_of_work_mock,
        )

        command = NewUserRegistrationCommandDto(
            name=faker.name(),
            email=faker.email(),
            password=faker.password(
                length=16,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ),
        )

        with pytest.raises(UserAlreadyExistsException):
            await use_case.execute(command)

        user_unit_of_work_mock.users.find_by_email.assert_awaited_once()
        password_hash_outbound_mock.hash.assert_not_called()
        user_unit_of_work_mock.users.save.assert_not_awaited()
        user_unit_of_work_mock.commit.assert_not_awaited()

    @pytest.mark.parametrize(
        "name",
        [
            "",
            "ab",
            "a" * 101,
        ],
    )
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_name_is_invalid(
        self,
        faker: Faker,
        name: str,
        logger_factory_outbound_mock: Mock,
        password_hash_outbound_mock: Mock,
        user_unit_of_work_mock: AsyncMock,
    ) -> None:

        use_case = NewUserRegistrationUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            password_hash_outbound=password_hash_outbound_mock,
            user_unit_of_work=user_unit_of_work_mock,
        )

        command = NewUserRegistrationCommandDto(
            name=name,
            email=faker.email(),
            password=faker.password(
                length=16,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ),
        )

        with pytest.raises(BaseDomainException):
            await use_case.execute(command)

        user_unit_of_work_mock.users.find_by_email.assert_not_awaited()
        password_hash_outbound_mock.hash.assert_not_called()
        user_unit_of_work_mock.users.save.assert_not_awaited()
        user_unit_of_work_mock.commit.assert_not_awaited()

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
        user_unit_of_work_mock: AsyncMock,
    ) -> None:

        use_case = NewUserRegistrationUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            password_hash_outbound=password_hash_outbound_mock,
            user_unit_of_work=user_unit_of_work_mock,
        )

        command = NewUserRegistrationCommandDto(
            name=faker.name(),
            email=email,
            password=faker.password(
                length=16,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ),
        )

        with pytest.raises(BaseDomainException):
            await use_case.execute(command)

        user_unit_of_work_mock.users.find_by_email.assert_not_awaited()
        password_hash_outbound_mock.hash.assert_not_called()
        user_unit_of_work_mock.users.save.assert_not_awaited()
        user_unit_of_work_mock.commit.assert_not_awaited()

    @pytest.mark.parametrize(
        "password",
        [
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
        user_unit_of_work_mock: AsyncMock,
    ) -> None:

        use_case = NewUserRegistrationUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            password_hash_outbound=password_hash_outbound_mock,
            user_unit_of_work=user_unit_of_work_mock,
        )

        command = NewUserRegistrationCommandDto(
            name=faker.name(),
            email=faker.email(),
            password=password,
        )

        with pytest.raises(BaseDomainException):
            await use_case.execute(command)

        user_unit_of_work_mock.users.find_by_email.assert_not_awaited()
        password_hash_outbound_mock.hash.assert_not_called()
        user_unit_of_work_mock.users.save.assert_not_awaited()
        user_unit_of_work_mock.commit.assert_not_awaited()
