from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from faker import Faker

from src.modules.books.application.dtos.get_book_catalog_dto import (
    GetBookCatalogCommandDto,
    GetBookCatalogResponseDto,
)
from src.modules.books.application.use_cases.get_book_catalog_use_case import (
    GetBookCatalogUseCase,
)
from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.enums.book_catalog_sort_by_enum import (
    BookCatalogSortByEnum,
)
from src.modules.books.domain.value_objects.author_vo import AuthorVO
from src.modules.books.domain.value_objects.book_catalog_cache_key_vo import (
    BookCatalogCacheKeyVO,
)
from src.modules.books.domain.value_objects.book_catalog_cache_value_vo import (
    BookCatalogCacheValueVO,
)
from src.modules.books.domain.value_objects.book_catalog_query_vo import (
    BookCatalogQueryVO,
)
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.domain.value_objects.published_year_vo import PublishedYearVO
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.modules.books.domain.value_objects.total_copies_vo import TotalCopiesVO
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO

VALID_ISBN_13 = "9780306406157"
_CACHE_TTL_SECONDS = 600


def _build_book(
    faker: Faker,
    title: str | None = None,
    author: str | None = None,
    isbn: str = VALID_ISBN_13,
    published_year: int = 2020,
    total_copies: int = 5,
) -> BookEntity:
    return BookEntity.create(
        title=TitleVO(title if title is not None else faker.sentence(nb_words=4)),
        isbn=IsbnVO(isbn),
        author=AuthorVO(author if author is not None else faker.name()),
        published_year=PublishedYearVO(published_year),
        total_copies=TotalCopiesVO(total_copies),
    )


def _build_command(
    title: str | None = None,
    author: str | None = None,
    isbn: str | None = None,
    is_available: bool | None = None,
    sort_by: Any = None,
    sort_order: Any = None,
    page: int = 1,
    page_size: int = 20,
) -> GetBookCatalogCommandDto:
    return GetBookCatalogCommandDto(
        title=title,
        author=author,
        isbn=isbn,
        is_available=is_available,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


class TestGetBookCatalogUseCase:
    @pytest.mark.asyncio
    async def test_should_return_catalog_from_database_when_cache_miss(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        cache_outbound_mock.get.return_value = None
        books = [_build_book(faker), _build_book(faker)]
        book_unit_of_work_mock.books.find_catalog.return_value = (books, 2)

        use_case = GetBookCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
        )

        command = _build_command(page=1, page_size=20)
        response = await use_case.execute(command)

        expected_query = BookCatalogQueryVO(
            title=None,
            author=None,
            isbn=None,
            is_available=None,
            sort_by=None,
            sort_order=None,
            page=1,
            page_size=20,
        )
        expected_key = BookCatalogCacheKeyVO.from_filters(expected_query)
        expected_response = GetBookCatalogResponseDto.response(
            books=books, total=2, page=1, page_size=20
        )

        assert response == expected_response

        cache_outbound_mock.get.assert_awaited_once_with(expected_key)
        book_unit_of_work_mock.books.find_catalog.assert_awaited_once_with(
            expected_query
        )

        cache_outbound_mock.set.assert_awaited_once()
        entry = cache_outbound_mock.set.await_args.args[0]

        assert isinstance(entry, CacheEntryVO)
        assert entry.key == expected_key
        assert entry.ttl == CacheTTLVO(seconds=_CACHE_TTL_SECONDS)
        assert entry.value == expected_response.to_cache_value()

        logger = logger_factory_outbound_mock.get_logger.return_value
        logger.debug.assert_any_call(
            "Cache MISS while retrieving the book catalog.",
            cache_key=expected_key.value(),
        )
        logger.debug.assert_any_call("Book catalog successfully retrieved.")

    @pytest.mark.asyncio
    async def test_should_return_catalog_from_cache_when_cache_hit(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        cached_value = BookCatalogCacheValueVO(
            items=(
                {
                    "id": faker.uuid4(),
                    "title": faker.sentence(nb_words=4),
                    "isbn": VALID_ISBN_13,
                    "author": faker.name(),
                    "published_year": 2020,
                    "total_copies": 5,
                    "available_copies": 5,
                    "created_at": faker.date_time().isoformat(),
                    "updated_at": faker.date_time().isoformat(),
                },
            ),
            total=1,
            page=1,
            page_size=20,
            total_pages=1,
        )
        cache_outbound_mock.get.return_value = cached_value

        use_case = GetBookCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
        )

        command = _build_command()
        response = await use_case.execute(command)

        expected_query = BookCatalogQueryVO(
            title=None,
            author=None,
            isbn=None,
            is_available=None,
            sort_by=None,
            sort_order=None,
            page=1,
            page_size=20,
        )
        expected_key = BookCatalogCacheKeyVO.from_filters(expected_query)

        assert response == GetBookCatalogResponseDto.from_cache_value(cached_value)

        cache_outbound_mock.get.assert_awaited_once_with(expected_key)
        book_unit_of_work_mock.books.find_catalog.assert_not_awaited()
        cache_outbound_mock.set.assert_not_awaited()

        logger = logger_factory_outbound_mock.get_logger.return_value
        logger.debug.assert_any_call(
            "Cache HIT while retrieving the book catalog.",
            cache_key=expected_key.value(),
        )

    @pytest.mark.asyncio
    async def test_should_build_query_with_provided_filters_and_sorting(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        cache_outbound_mock.get.return_value = None
        book_unit_of_work_mock.books.find_catalog.return_value = ([], 0)

        use_case = GetBookCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
        )

        title = faker.sentence(nb_words=4)
        author = faker.name()

        command = _build_command(
            title=title,
            author=author,
            isbn=VALID_ISBN_13,
            is_available=True,
            sort_by=BookCatalogSortByEnum.PUBLISHED_YEAR,
            sort_order=SortOrderEnum.DESC,
            page=2,
            page_size=10,
        )

        await use_case.execute(command)

        expected_query = BookCatalogQueryVO(
            title=TitleVO(title),
            author=AuthorVO(author),
            isbn=IsbnVO(VALID_ISBN_13),
            is_available=True,
            sort_by=BookCatalogSortByEnum.PUBLISHED_YEAR,
            sort_order=SortOrderEnum.DESC,
            page=2,
            page_size=10,
        )

        book_unit_of_work_mock.books.find_catalog.assert_awaited_once_with(
            expected_query
        )
        cache_outbound_mock.get.assert_awaited_once_with(
            BookCatalogCacheKeyVO.from_filters(expected_query)
        )

    @pytest.mark.asyncio
    async def test_should_treat_false_is_available_as_no_filter(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        # NOTE: the use case only reassigns `is_available` when it is truthy
        # (`command.is_available if command.is_available else None`), so an
        # explicit `False` is currently indistinguishable from "not provided".
        # This test documents that existing behavior.
        cache_outbound_mock.get.return_value = None
        book_unit_of_work_mock.books.find_catalog.return_value = ([], 0)

        use_case = GetBookCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
        )

        command = _build_command(is_available=False)

        await use_case.execute(command)

        used_query = book_unit_of_work_mock.books.find_catalog.await_args.args[0]

        assert used_query.is_available is None

    @pytest.mark.asyncio
    async def test_should_raise_exception_and_skip_cache_and_database_when_title_is_invalid(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetBookCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
        )

        command = _build_command(title="ab")

        with pytest.raises(BaseDomainException):
            await use_case.execute(command)

        cache_outbound_mock.get.assert_not_awaited()
        cache_outbound_mock.set.assert_not_awaited()
        book_unit_of_work_mock.books.find_catalog.assert_not_awaited()

        logger = logger_factory_outbound_mock.get_logger.return_value
        logger.warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_author_is_invalid(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetBookCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
        )

        command = _build_command(author="ab")

        with pytest.raises(BaseDomainException):
            await use_case.execute(command)

        cache_outbound_mock.get.assert_not_awaited()
        book_unit_of_work_mock.books.find_catalog.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_isbn_is_invalid(
        self,
        faker: Faker,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetBookCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
        )

        command = _build_command(isbn="123")

        with pytest.raises(BaseDomainException):
            await use_case.execute(command)

        cache_outbound_mock.get.assert_not_awaited()
        book_unit_of_work_mock.books.find_catalog.assert_not_awaited()

    @pytest.mark.parametrize(
        "is_available",
        [
            "yes",
            1,
        ],
    )
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_is_available_is_not_a_boolean(
        self,
        faker: Faker,
        is_available: Any,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetBookCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
        )

        command = _build_command(is_available=is_available)

        with pytest.raises(BaseDomainException):
            await use_case.execute(command)

        cache_outbound_mock.get.assert_not_awaited()
        book_unit_of_work_mock.books.find_catalog.assert_not_awaited()

    @pytest.mark.parametrize("page", [0, -1, True])
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_page_is_invalid(
        self,
        faker: Faker,
        page: Any,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetBookCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
        )

        command = _build_command(page=page)

        with pytest.raises(BaseDomainException):
            await use_case.execute(command)

        cache_outbound_mock.get.assert_not_awaited()
        book_unit_of_work_mock.books.find_catalog.assert_not_awaited()

    @pytest.mark.parametrize("page_size", [0, -1, True, 101])
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_page_size_is_invalid(
        self,
        faker: Faker,
        page_size: Any,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetBookCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
        )

        command = _build_command(page_size=page_size)

        with pytest.raises(BaseDomainException):
            await use_case.execute(command)

        cache_outbound_mock.get.assert_not_awaited()
        book_unit_of_work_mock.books.find_catalog.assert_not_awaited()

    @pytest.mark.parametrize("sort_by", ["invalid_field", "name"])
    @pytest.mark.asyncio
    async def test_should_raise_value_error_when_sort_by_is_not_a_valid_option(
        self,
        faker: Faker,
        sort_by: str,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetBookCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
        )

        command = _build_command(sort_by=sort_by)

        with pytest.raises(ValueError):
            await use_case.execute(command)

        cache_outbound_mock.get.assert_not_awaited()
        book_unit_of_work_mock.books.find_catalog.assert_not_awaited()

    @pytest.mark.parametrize("sort_order", ["ascending", "descending"])
    @pytest.mark.asyncio
    async def test_should_raise_value_error_when_sort_order_is_not_a_valid_option(
        self,
        faker: Faker,
        sort_order: str,
        logger_factory_outbound_mock: Mock,
        book_unit_of_work_mock: AsyncMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        use_case = GetBookCatalogUseCase(
            logger_factory_outbound=logger_factory_outbound_mock,
            cache_outbound=cache_outbound_mock,
            book_unit_of_work=book_unit_of_work_mock,
        )

        command = _build_command(sort_order=sort_order)

        with pytest.raises(ValueError):
            await use_case.execute(command)

        cache_outbound_mock.get.assert_not_awaited()
        book_unit_of_work_mock.books.find_catalog.assert_not_awaited()
