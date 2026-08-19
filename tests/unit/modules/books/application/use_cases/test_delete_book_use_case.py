from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from faker import Faker

from src.modules.books.application.dtos.delete_book_dto import DeleteBookCommandDto
from src.modules.books.application.use_cases.delete_book_use_case import (
    DeleteBookUseCase,
)
from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.exceptions.book_exception import BookNotFoundException
from src.modules.books.domain.value_objects.author_vo import AuthorVO
from src.modules.books.domain.value_objects.book_catalog_cache_key import (
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

VALID_ISBN_13 = "9780306406157"


def _build_existing_book(faker: Faker) -> BookEntity:
    return BookEntity.create(
        title=TitleVO(faker.sentence(nb_words=4)),
        isbn=IsbnVO(VALID_ISBN_13),
        author=AuthorVO(faker.name()),
        published_year=PublishedYearVO(2020),
        total_copies=TotalCopiesVO(5),
    )


def _build_command(book_id: UUID) -> DeleteBookCommandDto:
    return DeleteBookCommandDto(book_id=book_id)


def _build_authenticated_user(
    faker: Faker, role: UserRoleEnum = UserRoleEnum.LIBRARIAN
) -> AuthenticatedUserCommandDto:
    return AuthenticatedUserCommandDto(id=UUID(faker.uuid4()), role=role)


class TestDeleteBookUseCase:
    @pytest.mark.asyncio
    async def test_should_delete_book_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        existing_book = _build_existing_book(faker)
        book_unit_of_work_mock.books.find_by_id.return_value = existing_book

        use_case = DeleteBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(book_id=existing_book.id)
        authenticated_user = _build_authenticated_user(faker)

        await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.find_by_id.assert_awaited_once_with(
            existing_book.id
        )
        book_unit_of_work_mock.books.delete.assert_awaited_once_with(existing_book.id)
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
        use_case = DeleteBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(book_id=uuid4())
        authenticated_user = _build_authenticated_user(faker, role=UserRoleEnum.MEMBER)

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.find_by_id.assert_not_awaited()
        book_unit_of_work_mock.books.delete.assert_not_awaited()
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

        use_case = DeleteBookUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = _build_command(book_id=uuid4())
        authenticated_user = _build_authenticated_user(faker)

        with pytest.raises(BookNotFoundException):
            await use_case.execute(command, authenticated_user)

        book_unit_of_work_mock.books.find_by_id.assert_awaited_once()
        book_unit_of_work_mock.books.delete.assert_not_awaited()
        book_unit_of_work_mock.commit.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()
