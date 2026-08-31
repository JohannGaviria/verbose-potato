"""This module contains the use case composition."""

from src.modules.loans.application.use_cases.get_loan_catalog_use_case import (
    GetLoanCatalogUseCase,
)
from src.modules.loans.application.use_cases.get_my_loans_use_case import (
    GetMyLoansUseCase,
)
from src.modules.loans.application.use_cases.recording_loan_use_case import (
    RecordingLoanUseCase,
)
from src.modules.loans.application.use_cases.returning_loan_use_case import (
    ReturningLoanUseCase,
)
from src.modules.loans.presentation.compositions.infrastructure_composition import (
    get_loan_cache_invalidation_outbound,
    get_loan_catalog_cache_outbound,
    get_loan_unit_of_work,
    get_member_loan_cache_outbound,
)
from src.shared.presentation.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
)


def get_recording_loan_use_case() -> RecordingLoanUseCase:
    """Get the RecordingLoanUseCase instance.

    Returns:
        RecordingLoanUseCase: The RecordingLoanUseCase instance.
    """
    return RecordingLoanUseCase(
        logger_factory_outbound=get_logger_factory_outbound(),
        loan_unit_of_work=get_loan_unit_of_work(),
        loan_cache_invalidation_outbound=get_loan_cache_invalidation_outbound(),
    )


def get_returning_loan_use_case() -> ReturningLoanUseCase:
    """Get the ReturningLoanUseCase instance.

    Returns:
        ReturningLoanUseCase: The ReturningLoanUseCase instance.
    """
    return ReturningLoanUseCase(
        logger_factory_outbound=get_logger_factory_outbound(),
        loan_unit_of_work=get_loan_unit_of_work(),
        loan_cache_invalidation_outbound=get_loan_cache_invalidation_outbound(),
    )


def get_get_my_loans_use_case() -> GetMyLoansUseCase:
    """Get the GetMyLoansUseCase instance.

    Returns:
        GetMyLoansUseCase: The GetMyLoansUseCase instance.
    """
    return GetMyLoansUseCase(
        logger_factory_outbound=get_logger_factory_outbound(),
        cache_outbound=get_member_loan_cache_outbound(),
        loan_unit_of_work=get_loan_unit_of_work(),
    )


def get_get_loan_catalog_use_case() -> GetLoanCatalogUseCase:
    """Get the GetLoanCatalogUseCase instance.

    Returns:
        GetLoanCatalogUseCase: The GetLoanCatalogUseCase instance.
    """
    return GetLoanCatalogUseCase(
        logger_factory_outbound=get_logger_factory_outbound(),
        cache_outbound=get_loan_catalog_cache_outbound(),
        loan_unit_of_work=get_loan_unit_of_work(),
    )
