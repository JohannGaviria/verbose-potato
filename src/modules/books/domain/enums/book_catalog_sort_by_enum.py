"""This module contains the book catalog sort by enum."""

from enum import StrEnum


class BookCatalogSortByEnum(StrEnum):
    """Enumeration representing the available sorting fields for the book catalog.

    Attributes:
        TITLE (str): Sort books by their title.
        PUBLISHED_YEAR (str): Sort books by their publication year.
    """

    TITLE = "title"
    PUBLISHED_YEAR = "published_year"
