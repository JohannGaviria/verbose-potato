"""This module contains the get book catalog use case."""

from src.modules.books.application.dtos.get_book_catalog_dto import (
    GetBookCatalogCommandDto,
    GetBookCatalogResponseDto,
)
from src.modules.books.domain.enums.book_catalog_sort_by_enum import (
    BookCatalogSortByEnum,
)
from src.modules.books.domain.ports.unit_of_work.book_unit_of_work_port import (
    BookUnitOfWorkPort,
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
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException
from src.shared.domain.ports.outbound.cache_outbound_port import CacheOutboundPort
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO

_BOOK_CATALOG_CACHE_TTL_SECONDS = 600  # 10 Minutes


class GetBookCatalogUseCase:
    """Get the paginated book catalog use case."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        cache_outbound: CacheOutboundPort[BookCatalogCacheValueVO],
        book_unit_of_work: BookUnitOfWorkPort,
    ) -> None:
        """Initializes the GetBookCatalogUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
            cache_outbound (CacheOutboundPort[BookCatalogCacheValueVO]): Outbound used to create
                the cache instance.
            book_unit_of_work (BookUnitOfWorkPort): Unit of work used to persist book entities.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self._cache_outbound = cache_outbound
        self._book_unit_of_work = book_unit_of_work

    async def execute(
        self,
        command: GetBookCatalogCommandDto,
    ) -> GetBookCatalogResponseDto:
        """Execute the get book catalog use case.

        Args:
            command (GetBookCatalogCommandDto): Data required to execute the get book catalog use case.

        Returns:
            GetBookCatalogResponseDto: The response DTO for the get book catalog.
        """
        self._logger.debug("Executing: get book catalog use case.")

        try:
            title = TitleVO(command.title) if command.title else None
            author = AuthorVO(command.author) if command.author else None
            isbn = IsbnVO(command.isbn) if command.isbn else None
            is_available = command.is_available if command.is_available else None
            sort_by = (
                BookCatalogSortByEnum(command.sort_by) if command.sort_by else None
            )
            sort_order = (
                SortOrderEnum(command.sort_order) if command.sort_order else None
            )

            query = BookCatalogQueryVO(
                title=title,
                author=author,
                isbn=isbn,
                is_available=is_available,
                sort_by=sort_by,
                sort_order=sort_order,
                page=command.page,
                page_size=command.page_size,
            )
            cache_key = BookCatalogCacheKeyVO.from_filters(query)
            cached_value = await self._cache_outbound.get(cache_key)

            if cached_value is not None:
                self._logger.debug(
                    "Cache HIT while retrieving the book catalog.",
                    cache_key=cache_key.value(),
                )
                return GetBookCatalogResponseDto.from_cache_value(cached_value)

            self._logger.debug(
                "Cache MISS while retrieving the book catalog.",
                cache_key=cache_key.value(),
            )

            async with self._book_unit_of_work as uow:
                books, total = await uow.books.find_catalog(query)

            response = GetBookCatalogResponseDto.response(
                books=books,
                total=total,
                page=query.page,
                page_size=query.page_size,
            )

            entry = CacheEntryVO(
                key=cache_key,
                ttl=CacheTTLVO(seconds=_BOOK_CATALOG_CACHE_TTL_SECONDS),
                value=response.to_cache_value(),
            )
            await self._cache_outbound.set(entry)

            self._logger.debug("Book catalog successfully retrieved.")

            return response

        except BaseDomainException as exc:
            self._logger.warning(
                "Business rule violated while get book catalog.",
                error=str(exc),
            )
            raise
        finally:
            self._logger.debug("Executed: get book catalog use case.")
