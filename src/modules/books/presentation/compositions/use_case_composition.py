"""This module contains the use case composition."""

from src.modules.books.application.use_cases.delete_book_use_case import (
    DeleteBookUseCase,
)
from src.modules.books.application.use_cases.get_book_catalog_use_case import (
    GetBookCatalogUseCase,
)
from src.modules.books.application.use_cases.registration_new_book_use_case import (
    RegistrationNewBookUseCase,
)
from src.modules.books.application.use_cases.update_book_use_case import (
    UpdateBookUseCase,
)
from src.modules.books.presentation.compositions.infrastructure_composition import (
    get_book_cache_outbound,
    get_book_unit_of_work,
)
from src.shared.presentation.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
)


def get_registration_new_book_use_case() -> RegistrationNewBookUseCase:
    """Get the RegistrationNewBookUseCase instance.

    Returns:
        RegistrationNewBookUseCase: The RegistrationNewBookUseCase instance.
    """
    return RegistrationNewBookUseCase(
        logger_factory_outbound=get_logger_factory_outbound(),
        book_unit_of_work=get_book_unit_of_work(),
        cache_outbound=get_book_cache_outbound(),
    )


def get_update_book_use_case() -> UpdateBookUseCase:
    """Get the UpdateBookUseCase instance.

    Returns:
        UpdateBookUseCase: The UpdateBookUseCase instance.
    """
    return UpdateBookUseCase(
        logger_factory_outbound=get_logger_factory_outbound(),
        book_unit_of_work=get_book_unit_of_work(),
        cache_outbound=get_book_cache_outbound(),
    )


def get_delete_book_use_case() -> DeleteBookUseCase:
    """Get the DeleteBookUseCase instance.

    Returns:
        DeleteBookUseCase: The DeleteBookUseCase instance.
    """
    return DeleteBookUseCase(
        logger_factory_outbound=get_logger_factory_outbound(),
        book_unit_of_work=get_book_unit_of_work(),
        cache_outbound=get_book_cache_outbound(),
    )


def get_get_book_catalog_use_case() -> GetBookCatalogUseCase:
    """Get the GetBookCatalogUseCase instance.

    Returns:
        GetBookCatalogUseCase: The GetBookCatalogUseCase instance.
    """
    return GetBookCatalogUseCase(
        logger_factory_outbound=get_logger_factory_outbound(),
        book_unit_of_work=get_book_unit_of_work(),
        cache_outbound=get_book_cache_outbound(),
    )
