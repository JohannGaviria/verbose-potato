"""This module contains the use case composition."""

from src.modules.auth.application.use_cases.create_first_librarian_use_case import (
    CreateFirstLibrarianUseCase,
)
from src.modules.auth.application.use_cases.login_use_case import LoginUseCase
from src.modules.auth.application.use_cases.new_user_registration_use_case import (
    NewUserRegistrationUseCase,
)
from src.modules.auth.presentation.compositions.infrastructure_composition import (
    get_password_hash_outbound,
    get_token_generator_outbound,
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


def get_new_user_registration_use_case() -> NewUserRegistrationUseCase:
    """Get the NewUserRegistrationUseCase instance.

    Returns:
        NewUserRegistrationUseCase: The NewUserRegistrationUseCase instance.
    """
    return NewUserRegistrationUseCase(
        logger_factory_outbound=get_logger_factory_outbound(),
        password_hash_outbound=get_password_hash_outbound(),
        user_unit_of_work=get_user_unit_of_work(),
    )


def get_login_use_case() -> LoginUseCase:
    """Get the LoginUseCase instance.

    Returns:
        LoginUseCase: The LoginUseCase instance.
    """
    return LoginUseCase(
        logger_factory_outbound=get_logger_factory_outbound(),
        user_unit_of_work=get_user_unit_of_work(),
        password_hash_outbound=get_password_hash_outbound(),
        token_generator_outbound=get_token_generator_outbound(),
    )
