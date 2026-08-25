"""This module contains the sort order enum."""

from enum import StrEnum


class SortOrderEnum(StrEnum):
    """Enumeration representing the different sort orders.

    Attributes:
        ASC (str): Sort order for ascending order.
        DESC (str): Sort order for descending order.
    """

    ASC = "asc"
    DESC = "desc"
