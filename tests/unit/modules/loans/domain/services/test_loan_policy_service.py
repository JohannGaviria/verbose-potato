import pytest

from src.modules.loans.domain.constants.loan_constant import MAX_ACTIVE_LOANS_PER_MEMBER
from src.modules.loans.domain.exceptions.loan_exception import (
    MaximumActiveLoansExceededException,
)
from src.modules.loans.domain.services.loan_policy_service import LoanPolicyService


class TestLoanPolicyService:
    @pytest.mark.parametrize(
        "active_loans",
        list(range(MAX_ACTIVE_LOANS_PER_MEMBER)),
    )
    def test_should_not_raise_when_active_loans_are_below_the_maximum(
        self, active_loans: int
    ) -> None:
        LoanPolicyService.ensure_member_can_register_loan(active_loans)

    def test_should_raise_exception_when_active_loans_equal_the_maximum(self) -> None:
        with pytest.raises(MaximumActiveLoansExceededException):
            LoanPolicyService.ensure_member_can_register_loan(
                MAX_ACTIVE_LOANS_PER_MEMBER
            )

    def test_should_raise_exception_when_active_loans_exceed_the_maximum(self) -> None:
        with pytest.raises(MaximumActiveLoansExceededException):
            LoanPolicyService.ensure_member_can_register_loan(
                MAX_ACTIVE_LOANS_PER_MEMBER + 1
            )

    def test_should_be_usable_without_instantiating_the_service(self) -> None:
        LoanPolicyService.ensure_member_can_register_loan(0)
