"""This module contains the runner composition."""

from src.config import settings
from src.modules.auth.application.dtos.create_first_librarian_dto import (
    CreateFirstLibrarianCommandDto,
)
from src.modules.auth.presentation.compositions.use_case_composition import (
    get_create_first_librarian_use_case,
)
from src.modules.auth.presentation.system.runners.create_first_librarian_runner import (
    CreateFirstLibrarianRunner,
)
from src.shared.presentation.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
)


def get_create_first_librarian_runner() -> CreateFirstLibrarianRunner:
    """Get the CreateFirstLibrarianRunner instance.

    Returns:
        CreateFirstLibrarianRunner: The CreateFirstLibrarianRunner instance.
    """
    return CreateFirstLibrarianRunner(
        logger_factory_outbound=get_logger_factory_outbound(),
        create_first_librarian_use_case=get_create_first_librarian_use_case(),
        data=CreateFirstLibrarianCommandDto(
            name=settings.FIRST_LIBRARIES_NAME,
            email=settings.FIRST_LIBRARIES_EMAIL,
            password=settings.FIRST_LIBRARIES_PASSWORD,
        ),
    )
