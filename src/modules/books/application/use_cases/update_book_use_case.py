"""This module contains the update book use case."""

from src.modules.books.application.dtos.update_book_dto import (
    UpdateBookCommandDto,
    UpdateBookResponseDto,
)
from src.modules.books.domain.exceptions.book_exception import BookNotFoundException
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
from src.modules.books.domain.value_objects.published_year_vo import PublishedYearVO
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.modules.books.domain.value_objects.total_copies_vo import TotalCopiesVO
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException
from src.shared.domain.ports.outbound.cache_outbound_port import CacheOutboundPort
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.services.authorization_service import AuthorizationService


class UpdateBookUseCase:
    """Update book use case."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        book_unit_of_work: BookUnitOfWorkPort,
        cache_outbound: CacheOutboundPort[BookCatalogCacheValueVO],
    ) -> None:
        """Initialize the UpdateBookUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
            book_unit_of_work (BookUnitOfWorkPort): Unit of work used to persist book entities.
            cache_outbound (CacheOutboundPort[BookCatalogCacheValueVO]): Factory used to create
                the cache instance.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self._book_unit_of_work = book_unit_of_work
        self._cache_outbound = cache_outbound
        self._authorization_service = AuthorizationService()

    async def execute(
        self,
        command: UpdateBookCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> UpdateBookResponseDto:
        """Execute the update book use case.

        Args:
            command (UpdateBookCommandDto): Data required to update the book.
            authenticated_user (AuthenticatedUserCommandDto): Data required to authenticated user.

        Returns:
            UpdateBookResponseDto: The response DTO for the update book.
        """
        self._logger.info(
            "Executing: Update book use case.",
            book_id=command.book_id,
        )

        try:
            self._authorization_service.assert_role(
                authenticated_user.role, UserRoleEnum.LIBRARIAN
            )

            title = TitleVO(command.title) if command.title is not None else None
            author = AuthorVO(command.author) if command.author is not None else None
            published_year = (
                PublishedYearVO(command.published_year)
                if command.published_year is not None
                else None
            )
            total_copies = (
                TotalCopiesVO(command.total_copies)
                if command.total_copies is not None
                else None
            )

            async with self._book_unit_of_work as uow:
                exists_book = await uow.books.find_by_id(command.book_id)

                if exists_book is None:
                    self._logger.warning(
                        "Book not found.",
                        book_id=command.book_id,
                    )
                    raise BookNotFoundException()

                entity = exists_book.update(
                    title=title,
                    author=author,
                    published_year=published_year,
                    total_copies=total_copies,
                )

                book = await uow.books.update(entity)
                await uow.commit()

                key = BookCatalogCacheKeyVO.pattern()
                await self._cache_outbound.delete(key)

            self._logger.debug("Book successfully updated.", book_id=command.book_id)

            return UpdateBookResponseDto.response(book)

        except BaseDomainException as exc:
            self._logger.warning(
                "Business rule violated while registering a new book.",
                error=str(exc),
            )
            raise
        finally:
            self._logger.info("Executed: Update book use case.")
