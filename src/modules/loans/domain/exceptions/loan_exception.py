"""This module contains the loan exception."""

from uuid import UUID

from src.shared.domain.exceptions.base_domain_exception import BaseDomainException


class MemberAlreadyHasActiveLoanException(BaseDomainException):
    """Exception raised when a user is already active in a loan."""

    def __init__(self, member_id: UUID, book_id: UUID) -> None:
        """Initialize the MemberAlreadyHasActiveLoanException.

        Args:
            member_id (UUID): The member id of the loan.
            book_id (UUID): The book id of the loan.
        """
        self.member_id = member_id
        self.book_id = book_id
        super().__init__("Member already has active loan.")


class MaximumActiveLoansExceededException(BaseDomainException):
    """Exception raised when a user has exceeded the maximum number of active loans."""

    def __init__(self) -> None:
        """Initialize the MaximumActiveLoansExceededException."""
        super().__init__("Maximum active loans exceeded.")


class LoanNotFoundException(BaseDomainException):
    """Exception raised when a loan cannot be found."""

    def __init__(self) -> None:
        """Initialize the LoanNotFoundException."""
        super().__init__("Loan cannot be found.")


class LoanAlreadyReturnedException(BaseDomainException):
    """Exception raised when a loan has already been returned."""

    def __init__(self, loan_id: UUID) -> None:
        """Initialize the LoanAlreadyReturnedException.

        Args:
            loan_id (UUID): The id of the loan that was already returned.
        """
        self.loan_id = loan_id
        super().__init__("Loan has already been returned.")


class InvalidMemberLoanQueryException(BaseDomainException):
    """Exception raised when the member loan query is invalid."""

    def __init__(self, error: str, filter: str | int | bool) -> None:
        """Initialize the InvalidMemberLoanQueryException.

        Args:
            error (str): The error message.
            filter (str | int | bool): The invalid filter for the member loans.
        """
        self.error = error
        self.filter = filter
        super().__init__("Invalid member loan query provided.")


class LoanRepositoryException(BaseDomainException):
    """Exception raised when the loan repository fails."""

    def __init__(self, error: str) -> None:
        """Initialize the LoanRepositoryException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Error while interacting with the loan repository.")
