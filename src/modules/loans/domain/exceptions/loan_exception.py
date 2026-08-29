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
