"""This module contains the loan status enum."""

from enum import StrEnum


class LoanStatusEnum(StrEnum):
    """Enumeration representing the loan status.

    Attributes:
        ACTIVE (str): The active loan status.
        RETURNED (str): The return loan status.
    """

    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
