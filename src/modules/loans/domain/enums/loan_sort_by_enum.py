"""This module contains the loan sort by enum."""

from enum import StrEnum


class LoanSortByEnum(StrEnum):
    """Enumeration representing the available sorting fields for the member loans.

    Attributes:
        LOANED_AT (str): Sort loans by their loaned date.
        RETURNED_AT (str): Sort loans by their returned date.
    """

    LOANED_AT = "loaned_at"
    RETURNED_AT = "returned_at"
