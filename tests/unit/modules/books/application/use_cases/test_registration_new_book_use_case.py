from datetime import date
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.books.application.dtos.registration_new_book_dto import (
    RegistrationNewBookCommandDto,
    RegistrationNewBookResponseDto,
)
from src.modules.books.application.use_cases.registration_new_book_use_case import (
    RegistrationNewBookUseCase,
)
from src.modules.books.domain.exceptions.book_exception import (
    ISBNAlreadyRegisteredException,
)
from src.modules.books.domain.value_objects.book_catalog_cache_key import (
    BookCatalogCacheKeyVO,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.authentication_authorization_exception import (
    InsufficientPermissionsException,
)
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException

VALID_ISBN_13 = "9780306406157"


def _build_command(
    faker: Faker,
    title: str | None = None,
    isbn: str | None = None,
    author: str | None = None,
    published_year: int | None = None,
    total_copies: int | None = None,
) -> RegistrationNewBookCommandDto:
    return RegistrationNewBookCommandDto(
        title=title if title is not None else faker.sentence(nb_words=4),
        isbn=isbn if isbn is not None else VALID_ISBN_13,
        author=author if author is not None else faker.name(),
        published_year=(published_year if published_year is not None else 2020),
        total_copies=total_copies if total_copies is not None else 5,
    )


def _build_authenticated_user(
    faker: Faker, role: UserRoleEnum = UserRoleEnum.LIBRARIAN
) -> AuthenticatedUserCommandDto:
    return AuthenticatedUserCommandDto(id=UUID(faker.uuid4()), role=role)


class TestRegistrationNewBookUseCase:
    @pytest.mark.asyncio
    async def test_should_register_book_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:

        title = faker.sentence(nb_words=4)
        isbn = VALID_ISBN_13
        author = faker.name()
        published_year = 2020
        total_copies = 5

        book_unit_of_work_mock.books.exists_by_isbn.return_value = False

        saved_book = Mock()
        saved_book.id = faker.uuid4()
        saved_book.title.value = title
        saved_book.isbn.value = isbn
        saved_book.author.value = author
        saved_book.published_year.value = published_year
        saved_book.total_copies.value = total_copies
        saved_book.available_copies = total_copies
        saved_book.created_at = faker.date_time()
        saved_book.updated_at = faker.date_time()

        book_unit_of_work_mock.books.save.return_value = saved_book

        use_case = RegistrationNewBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(
            faker,
            title=title,
            isbn=isbn,
            author=author,
            published_year=published_year,
            total_copies=total_copies,
        )
        authenticated_user = _build_authenticated_user(faker)

        response = await use_case.execute(command, authenticated_user)

        saved_entity = book_unit_of_work_mock.books.save.await_args.args[0]

        assert saved_entity.title.value == title
        assert saved_entity.isbn.value == isbn
        assert saved_entity.author.value == author
        assert saved_entity.published_year.value == published_year
        assert saved_entity.total_copies.value == total_copies

        assert response == RegistrationNewBookResponseDto.response(saved_book)

        book_unit_of_work_mock.books.exists_by_isbn.assert_awaited_once()
        book_unit_of_work_mock.commit.assert_awaited_once()
        cache_outbound_mock.delete.assert_awaited_once_with(
            BookCatalogCacheKeyVO.pattern()
        )

    @pytest.mark.asyncio
    async def test_should_raise_insufficient_permissions_exception_when_user_is_not_librarian(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:

        use_case = RegistrationNewBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(faker)
        authenticated_user = _build_authenticated_user(faker, role=UserRoleEnum.MEMBER)

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.exists_by_isbn.assert_not_awaited()
        book_unit_of_work_mock.books.save.assert_not_awaited()
        book_unit_of_work_mock.commit.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_isbn_already_registered_exception_when_isbn_is_registered(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:

        book_unit_of_work_mock.books.exists_by_isbn.return_value = True

        use_case = RegistrationNewBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(faker)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(ISBNAlreadyRegisteredException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.exists_by_isbn.assert_awaited_once()
        book_unit_of_work_mock.books.save.assert_not_awaited()
        book_unit_of_work_mock.commit.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.parametrize(
        "title",
        [
            "",
            "ab",
            "a" * 256,
        ],
    )
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_title_is_invalid(
        self,
        faker: Faker,
        title: str,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:

        use_case = RegistrationNewBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(faker, title=title)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(BaseDomainException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.exists_by_isbn.assert_not_awaited()
        book_unit_of_work_mock.books.save.assert_not_awaited()
        book_unit_of_work_mock.commit.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.parametrize(
        "isbn",
        [
            "",
            "123",
            "12345678901",
            "9780306406158",
        ],
    )
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_isbn_is_invalid(
        self,
        faker: Faker,
        isbn: str,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:

        use_case = RegistrationNewBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(faker, isbn=isbn)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(BaseDomainException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.exists_by_isbn.assert_not_awaited()
        book_unit_of_work_mock.books.save.assert_not_awaited()
        book_unit_of_work_mock.commit.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.parametrize(
        "author",
        [
            "",
            "ab",
            "a" * 101,
        ],
    )
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_author_is_invalid(
        self,
        faker: Faker,
        author: str,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:

        use_case = RegistrationNewBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(faker, author=author)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(BaseDomainException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.exists_by_isbn.assert_not_awaited()
        book_unit_of_work_mock.books.save.assert_not_awaited()
        book_unit_of_work_mock.commit.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_published_year_is_invalid(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:

        use_case = RegistrationNewBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        for published_year in (1449, date.today().year + 1, True):
            command = _build_command(faker, published_year=published_year)
            authenticated_user = _build_authenticated_user(faker)

            with pytest.raises(BaseDomainException):
                await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.exists_by_isbn.assert_not_awaited()
        book_unit_of_work_mock.books.save.assert_not_awaited()
        book_unit_of_work_mock.commit.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.parametrize(
        "total_copies",
        [
            0,
            -1,
            True,
        ],
    )
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_total_copies_is_invalid(
        self,
        faker: Faker,
        total_copies: int,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:

        use_case = RegistrationNewBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(faker, total_copies=total_copies)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(BaseDomainException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.exists_by_isbn.assert_not_awaited()
        book_unit_of_work_mock.books.save.assert_not_awaited()
        book_unit_of_work_mock.commit.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()
