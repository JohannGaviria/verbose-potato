"""This module contains the delete book use case."""

from src.modules.books.application.dtos.delete_book_dto import DeleteBookCommandDto
from src.modules.books.domain.exceptions.book_exception import (
    BookHasActiveLoansException,
    BookNotFoundException,
)
from src.modules.books.domain.ports.unit_of_work.book_unit_of_work_port import (
    BookUnitOfWorkPort,
)
from src.modules.books.domain.value_objects.book_catalog_cache_key_vo import (
    BookCatalogCacheKeyVO,
)
from src.modules.books.domain.value_objects.book_catalog_cache_value_vo import (
    BookCatalogCacheValueVO,
)
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


class DeleteBookUseCase:
    """Delete book use case."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        book_unit_of_work: BookUnitOfWorkPort,
        cache_outbound: CacheOutboundPort[BookCatalogCacheValueVO],
    ) -> None:
        """Initializes the DeleteBookUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
            book_unit_of_work (BookUnitOfWorkPort): Unit of work used to persist book entities.
            cache_outbound (CacheOutboundPort[BookCatalogCacheValueVO]): Outbound used to create
                the cache instance.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self._book_unit_of_work = book_unit_of_work
        self._cache_outbound = cache_outbound
        self._authorization_service = AuthorizationService()

    async def execute(
        self,
        command: DeleteBookCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> None:
        """Execute the delete book use case.

        Args:
            command (DeleteBookCommandDto): Data required to execute the delete book use case.
            authenticated_user (AuthenticatedUserCommandDto): Data required to authenticate the user.
        """
        self._logger.debug("Executing: delete book use case.")

        try:
            self._authorization_service.assert_role(
                authenticated_user.role, UserRoleEnum.LIBRARIAN
            )

            async with self._book_unit_of_work as uow:
                exists_book = await uow.books.find_by_id(command.book_id)

                if exists_book is None:
                    self._logger.warning(
                        "Book does not exist.", book_id=command.book_id
                    )
                    raise BookNotFoundException()

                if exists_book.has_active_loans():
                    self._logger.warning(
                        "Book has active loans.",
                        book_id=command.book_id,
                    )
                    raise BookHasActiveLoansException()

                await uow.books.delete(command.book_id)
                await uow.commit()

                key = BookCatalogCacheKeyVO.pattern()
                await self._cache_outbound.delete(key)

            self._logger.debug("Book successfully deleted.", book_id=command.book_id)

        except BaseDomainException as exc:
            self._logger.warning(
                "Business rule violated while delete book.",
                error=str(exc),
            )
            raise
        finally:
            self._logger.debug("Executed: delete book use case.")
