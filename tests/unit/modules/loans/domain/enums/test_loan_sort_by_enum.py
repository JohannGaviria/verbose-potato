from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum


class TestLoanSortByEnum:
    def test_should_have_loaned_at_value(self) -> None:
        assert LoanSortByEnum.LOANED_AT.value == "loaned_at"

    def test_should_have_returned_at_value(self) -> None:
        assert LoanSortByEnum.RETURNED_AT.value == "returned_at"
