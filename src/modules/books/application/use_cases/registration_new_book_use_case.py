"""This module contains the registration new book use case."""

from src.modules.books.application.dtos.registration_new_book_dto import (
    RegistrationNewBookCommandDto,
    RegistrationNewBookResponseDto,
)
from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.exceptions.book_exception import (
    ISBNAlreadyRegisteredException,
)
from src.modules.books.domain.ports.unit_of_work.book_unit_of_work_port import (
    BookUnitOfWorkPort,
)
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
from src.shared.domain.exceptions.base_domain_exception import BaseDomainException
from src.shared.domain.ports.outbound.cache_outbound_port import CacheOutboundPort
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.services.authorization_service import AuthorizationService


class RegistrationNewBookUseCase:
    """Registration new book."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        book_unit_of_work: BookUnitOfWorkPort,
        cache_outbound: CacheOutboundPort,
    ) -> None:
        """Initializes the RegistrationNewBookUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory used to create the logger instance.
            book_unit_of_work (BookUnitOfWorkPort): Unit of work used to persist book entities.
            cache_outbound (CacheOutboundPort): Outbound used to create the cache instance.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self._book_unit_of_work = book_unit_of_work
        self._cache_outbound = cache_outbound
        self._authorization_service = AuthorizationService()

    async def execute(
        self,
        command: RegistrationNewBookCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> RegistrationNewBookResponseDto:
        """Execute the registration new book use case.

        Args:
            command (RegistrationNewBookCommandDto): Data required to registration new book.
            authenticated_user (AuthenticatedUserCommandDto): Data required to authenticated user.

        Returns:
            RegistrationNewBookResponseDto: The response DTO for the registration new book.

        Raises:
            ISBNAlreadyRegisteredException: If the ISBN is already registered.
        """
        self._logger.debug("Executing: Registration new book use case.")

        try:
            self._authorization_service.assert_role(
                authenticated_user.role, UserRoleEnum.LIBRARIAN
            )

            title = TitleVO(command.title)
            isbn = IsbnVO(command.isbn)
            author = AuthorVO(command.author)
            published_year = PublishedYearVO(command.published_year)
            total_copies = TotalCopiesVO(command.total_copies)

            async with self._book_unit_of_work as uow:
                if await uow.books.exists_by_isbn(isbn):
                    self._logger.warning(
                        "A book with this ISBN is already registered.", isbn=isbn
                    )
                    raise ISBNAlreadyRegisteredException()

                entity = BookEntity.create(
                    title=title,
                    isbn=isbn,
                    author=author,
                    published_year=published_year,
                    total_copies=total_copies,
                )

                book = await uow.books.save(entity)
                await uow.commit()

                key = BookCatalogCacheKeyVO.pattern()
                await self._cache_outbound.delete(key)

            self._logger.debug("Book successfully registered.")
            return RegistrationNewBookResponseDto.response(book)

        except BaseDomainException as exc:
            self._logger.warning(
                "Business rule violated while registering a new book.",
                error=str(exc),
            )
            raise
        finally:
            self._logger.debug("Executed: Registration new book use case.")
