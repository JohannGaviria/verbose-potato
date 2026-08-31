"""This module contains the use case composition."""

from src.modules.loans.application.use_cases.recording_loan_use_case import (
    RecordingLoanUseCase,
)
from src.modules.loans.presentation.compositions.infrastructure_composition import (
    get_loan_cache_invalidation_outbound,
    get_loan_unit_of_work,
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
