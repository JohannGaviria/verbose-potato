"""This module contains the use case composition."""

from src.modules.auth.application.use_cases.create_first_librarian_use_case import (
    CreateFirstLibrarianUseCase,
)
from src.modules.auth.presentation.compositions.infrastructure_composition import (
    get_password_hash_outbound,
    get_user_unit_of_work,
)
from src.shared.presentation.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
)


def get_create_first_librarian_use_case() -> CreateFirstLibrarianUseCase:
    """Get the CreateFirstLibrarianUseCase instance.

    Returns:
        CreateFirstLibrarianUseCase: The CreateFirstLibrarianUseCase instance.
    """
    return CreateFirstLibrarianUseCase(
        logger_factory_outbound=get_logger_factory_outbound(),
        password_hash_outbound=get_password_hash_outbound(),
        user_unit_of_work=get_user_unit_of_work(),
    )
