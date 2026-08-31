"""This module contains the loan policy services."""

from src.modules.loans.domain.constants.loan_constant import MAX_ACTIVE_LOANS_PER_MEMBER
from src.modules.loans.domain.exceptions.loan_exception import (
    MaximumActiveLoansExceededException,
)


class LoanPolicyService:
    """Domain service for loan business rules."""

    @staticmethod
    def ensure_member_can_register_loan(active_loans: int) -> None:
        """Ensure that a member has not reached the active loan limit.

        Args:
            active_loans: Number of active loans currently held by the member.

        Raises:
            MaximumActiveLoansExceededException: If the member has reached
                the maximum number of active loans allowed.
        """
        if active_loans >= MAX_ACTIVE_LOANS_PER_MEMBER:
            raise MaximumActiveLoansExceededException()
