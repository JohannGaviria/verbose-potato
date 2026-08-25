from datetime import date
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from faker import Faker

from src.modules.books.application.dtos.update_book_dto import (
    UpdateBookCommandDto,
    UpdateBookResponseDto,
)
from src.modules.books.application.use_cases.update_book_use_case import (
    UpdateBookUseCase,
)
from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.exceptions.book_exception import (
    BookNotFoundException,
    InvalidTotalCopiesException,
)
from src.modules.books.domain.value_objects.author_vo import AuthorVO
from src.modules.books.domain.value_objects.book_catalog_cache_key_vo import (
    BookCatalogCacheKeyVO,
)
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.domain.value_objects.published_year_vo import PublishedYearVO
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.modules.books.domain.value_objects.total_copies_vo import TotalCopiesVO
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.authentication_authorization_exception import (
    InsufficientPermissionsException,
)
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException

VALID_ISBN_13 = "9780306406157"


def _build_existing_book(
    faker: Faker,
    title: str | None = None,
    author: str | None = None,
    published_year: int | None = None,
    total_copies: int | None = None,
) -> BookEntity:
    return BookEntity.create(
        title=TitleVO(title if title is not None else faker.sentence(nb_words=4)),
        isbn=IsbnVO(VALID_ISBN_13),
        author=AuthorVO(author if author is not None else faker.name()),
        published_year=PublishedYearVO(
            published_year if published_year is not None else 2020
        ),
        total_copies=TotalCopiesVO(total_copies if total_copies is not None else 5),
    )


def _build_command(
    book_id: UUID,
    title: str | None = None,
    author: str | None = None,
    published_year: int | None = None,
    total_copies: int | None = None,
) -> UpdateBookCommandDto:
    return UpdateBookCommandDto(
        book_id=book_id,
        title=title,
        author=author,
        published_year=published_year,
        total_copies=total_copies,
    )


def _build_authenticated_user(
    faker: Faker, role: UserRoleEnum = UserRoleEnum.LIBRARIAN
) -> AuthenticatedUserCommandDto:
    return AuthenticatedUserCommandDto(id=UUID(faker.uuid4()), role=role)


class TestUpdateBookUseCase:
    @pytest.mark.asyncio
    async def test_should_update_book_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        existing_book = _build_existing_book(faker)
        book_unit_of_work_mock.books.find_by_id.return_value = existing_book
        book_unit_of_work_mock.books.update.side_effect = lambda entity: entity

        use_case = UpdateBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        new_title = faker.sentence(nb_words=4)
        new_author = faker.name()
        new_published_year = 2021
        new_total_copies = 10

        command = _build_command(
            book_id=existing_book.id,
            title=new_title,
            author=new_author,
            published_year=new_published_year,
            total_copies=new_total_copies,
        )
        authenticated_user = _build_authenticated_user(faker)

        response = await use_case.execute(command, authenticated_user)

        updated_entity = book_unit_of_work_mock.books.update.await_args.args[0]

        assert updated_entity.id == existing_book.id
        assert updated_entity.isbn == existing_book.isbn
        assert updated_entity.title.value == new_title
        assert updated_entity.author.value == new_author
        assert updated_entity.published_year.value == new_published_year
        assert updated_entity.total_copies.value == new_total_copies

        assert response == UpdateBookResponseDto.response(updated_entity)

        book_unit_of_work_mock.books.find_by_id.assert_awaited_once_with(
            existing_book.id
        )
        book_unit_of_work_mock.books.update.assert_awaited_once()
        book_unit_of_work_mock.commit.assert_awaited_once()
        cache_outbound_mock.delete.assert_awaited_once_with(
            BookCatalogCacheKeyVO.pattern()
        )

    @pytest.mark.asyncio
    async def test_should_keep_unprovided_fields_unchanged_when_partial_update(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        existing_book = _build_existing_book(faker)
        book_unit_of_work_mock.books.find_by_id.return_value = existing_book
        book_unit_of_work_mock.books.update.side_effect = lambda entity: entity

        use_case = UpdateBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        new_title = faker.sentence(nb_words=4)
        command = _build_command(book_id=existing_book.id, title=new_title)
        authenticated_user = _build_authenticated_user(faker)

        await use_case.execute(command, authenticated_user)

        updated_entity = book_unit_of_work_mock.books.update.await_args.args[0]

        assert updated_entity.title.value == new_title
        assert updated_entity.author == existing_book.author
        assert updated_entity.published_year == existing_book.published_year
        assert updated_entity.total_copies == existing_book.total_copies

    @pytest.mark.asyncio
    async def test_should_raise_insufficient_permissions_exception_when_user_is_not_librarian(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = UpdateBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(book_id=uuid4(), title=faker.sentence(nb_words=4))
        authenticated_user = _build_authenticated_user(faker, role=UserRoleEnum.MEMBER)

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.find_by_id.assert_not_awaited()
        book_unit_of_work_mock.books.update.assert_not_awaited()
        book_unit_of_work_mock.commit.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_book_not_found_exception_when_book_does_not_exist(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        book_unit_of_work_mock.books.find_by_id.return_value = None

        use_case = UpdateBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(book_id=uuid4(), title=faker.sentence(nb_words=4))
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(BookNotFoundException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.find_by_id.assert_awaited_once()
        book_unit_of_work_mock.books.update.assert_not_awaited()
        book_unit_of_work_mock.commit.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_invalid_total_copies_exception_when_total_copies_is_less_than_available_copies(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        existing_book = _build_existing_book(faker, total_copies=5)
        book_unit_of_work_mock.books.find_by_id.return_value = existing_book

        use_case = UpdateBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(book_id=existing_book.id, total_copies=3)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(InvalidTotalCopiesException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.find_by_id.assert_awaited_once()
        book_unit_of_work_mock.books.update.assert_not_awaited()
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
        use_case = UpdateBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(book_id=uuid4(), title=title)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(BaseDomainException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.find_by_id.assert_not_awaited()
        book_unit_of_work_mock.books.update.assert_not_awaited()
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
        use_case = UpdateBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(book_id=uuid4(), author=author)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(BaseDomainException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.find_by_id.assert_not_awaited()
        book_unit_of_work_mock.books.update.assert_not_awaited()
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
        use_case = UpdateBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        for published_year in (1449, date.today().year + 1, True):
            command = _build_command(book_id=uuid4(), published_year=published_year)
            authenticated_user = _build_authenticated_user(faker)

            with pytest.raises(BaseDomainException):
                await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.find_by_id.assert_not_awaited()
        book_unit_of_work_mock.books.update.assert_not_awaited()
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
        use_case = UpdateBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(book_id=uuid4(), total_copies=total_copies)
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(BaseDomainException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.find_by_id.assert_not_awaited()
        book_unit_of_work_mock.books.update.assert_not_awaited()
        book_unit_of_work_mock.commit.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()
