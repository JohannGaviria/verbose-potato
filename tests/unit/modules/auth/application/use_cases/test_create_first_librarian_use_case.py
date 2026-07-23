from unittest.mock import AsyncMock, Mock

import pytest
from faker import Faker

from src.modules.auth.application.dtos.create_first_librarian_dto import (
    CreateFirstLibrarianCommandDto,
)
from src.modules.auth.application.use_cases.create_first_librarian_use_case import (
    CreateFirstLibrarianUseCase,
)
from src.modules.auth.domain.exceptions.user_exception import (
    LibrarianAlreadyExistsException,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.base_exception import BaseException


class TestCreateFirstLibrarianUseCase:
    @pytest.mark.asyncio
    async def test_should_create_first_librarian_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        password_hash_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
    ) -> None:

        name = faker.name()
        email = faker.email()
        password = faker.password(
            length=16, special_chars=True, digits=True, upper_case=True, lower_case=True
        )

        user_repository_mock.exists_librarian.return_value = False
        password_hash_outbound_mock.hash.return_value = "hashed-password"

        saved_user = Mock()
        saved_user.id = faker.uuid4()
        saved_user.name.value = name
        saved_user.email.value = email

        user_repository_mock.save.return_value = saved_user

        use_case = CreateFirstLibrarianUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            password_hash_outbound=password_hash_outbound_mock,
            user_repository=user_repository_mock,
        )

        command = CreateFirstLibrarianCommandDto(
            name=name, email=email, password=password
        )

        await use_case.execute(command)

        saved_entity = user_repository_mock.save.await_args.args[0]

        assert saved_entity.name.value == name
        assert saved_entity.email.value == email
        assert saved_entity.password == "hashed-password"
        assert saved_entity.role == UserRoleEnum.LIBRARIAN

    @pytest.mark.asyncio
    async def test_should_raise_librarian_already_exists_exception_when_a_librarian_already_exists(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        password_hash_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
    ) -> None:

        user_repository_mock.exists_librarian.return_value = True

        use_case = CreateFirstLibrarianUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            password_hash_outbound=password_hash_outbound_mock,
            user_repository=user_repository_mock,
        )

        command = CreateFirstLibrarianCommandDto(
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

        with pytest.raises(LibrarianAlreadyExistsException):
            await use_case.execute(command)

        user_repository_mock.exists_librarian.assert_awaited_once()
        password_hash_outbound_mock.hash.assert_not_called()
        user_repository_mock.save.assert_not_awaited()

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
        user_repository_mock: AsyncMock,
    ) -> None:

        use_case = CreateFirstLibrarianUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            password_hash_outbound=password_hash_outbound_mock,
            user_repository=user_repository_mock,
        )

        command = CreateFirstLibrarianCommandDto(
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

        with pytest.raises(BaseException):
            await use_case.execute(command)

        user_repository_mock.exists_librarian.assert_not_awaited()
        password_hash_outbound_mock.hash.assert_not_called()
        user_repository_mock.save.assert_not_awaited()

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
        user_repository_mock: AsyncMock,
    ) -> None:

        use_case = CreateFirstLibrarianUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            password_hash_outbound=password_hash_outbound_mock,
            user_repository=user_repository_mock,
        )

        command = CreateFirstLibrarianCommandDto(
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

        with pytest.raises(BaseException):
            await use_case.execute(command)

        user_repository_mock.exists_librarian.assert_not_awaited()
        password_hash_outbound_mock.hash.assert_not_called()
        user_repository_mock.save.assert_not_awaited()

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
        user_repository_mock: AsyncMock,
    ) -> None:

        use_case = CreateFirstLibrarianUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            password_hash_outbound=password_hash_outbound_mock,
            user_repository=user_repository_mock,
        )

        command = CreateFirstLibrarianCommandDto(
            name=faker.name(),
            email=faker.email(),
            password=password,
        )

        with pytest.raises(BaseException):
            await use_case.execute(command)

        user_repository_mock.exists_librarian.assert_not_awaited()
        password_hash_outbound_mock.hash.assert_not_called()
        user_repository_mock.save.assert_not_awaited()
