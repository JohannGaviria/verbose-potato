"""This module contains the book catalog query value object."""

from dataclasses import dataclass

from src.modules.books.domain.enums.book_catalog_sort_by_enum import (
    BookCatalogSortByEnum,
)
from src.modules.books.domain.exceptions.book_exception import (
    InvalidBookCatalogQueryException,
)
from src.modules.books.domain.value_objects.author_vo import AuthorVO
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.shared.domain.enums.sort_order_enum import SortOrderEnum
from src.shared.domain.value_objects.base_value_object import BaseValueObject

_MAX_PAGE_SIZE = 100


@dataclass(frozen=True, slots=True)
class BookCatalogQueryVO(BaseValueObject):
    """Value object representing the query parameters for the book catalog.

    Attributes:
        title (TitleVO | None): The title of the book catalog.
        author (AuthorVO  | None): The author of the book catalog.
        isbn (IsbnVO  | None): The ISBN of the book catalog.
        is_available (bool): Whether the book catalog is available.
        sort_by (BookCatalogSortByEnum): The sort by which book catalog is to be used.
        sort_order (SortOrderEnum): The sort order.
        page (int): The page of the book catalog.
        page_size (int): The page size of the book catalog.
    """

    title: TitleVO | None
    author: AuthorVO | None
    isbn: IsbnVO | None
    is_available: bool | None

    sort_by: BookCatalogSortByEnum | None
    sort_order: SortOrderEnum | None

    page: int
    page_size: int

    def _validate(self) -> None:
        """Validate the rules for book catalog query.

        The rules for book catalog query value object are:
        - Availability must be a boolean when provided.
        - Sort field must be a valid book catalog sort field.
        - Sort order must be a valid sort order.
        - Page must be an integer greater than or equal to 1.
        - Page size must be an integer between 1 and 100.

        Raises:
            InvalidBookCatalogQueryException: If the book catalog query does not
                meet the validation criteria.
        """
        if self.is_available is not None and not isinstance(self.is_available, bool):
            raise InvalidBookCatalogQueryException(
                "is_available must be a boolean.", self.is_available
            )
        if self.sort_by is not None and not isinstance(
            self.sort_by, BookCatalogSortByEnum
        ):
            raise InvalidBookCatalogQueryException(
                "sort_by must be one of: 'title', 'published_year'.",
                str(self.sort_by),
            )
        if self.sort_order is not None and not isinstance(
            self.sort_order, SortOrderEnum
        ):
            raise InvalidBookCatalogQueryException(
                "sort_order must be one of: 'asc', 'desc'.", str(self.sort_order)
            )
        if isinstance(self.page, bool) or not isinstance(self.page, int):
            raise InvalidBookCatalogQueryException(
                "page must be an integer.", self.page
            )
        if self.page < 1:
            raise InvalidBookCatalogQueryException(
                "page must be greater than or equal to 1.", self.page
            )
        if isinstance(self.page_size, bool) or not isinstance(self.page_size, int):
            raise InvalidBookCatalogQueryException(
                "page_size must be an integer.", self.page_size
            )
        if self.page_size < 1:
            raise InvalidBookCatalogQueryException(
                "page_size must be greater than or equal to 1.", self.page_size
            )
        if self.page_size > _MAX_PAGE_SIZE:
            raise InvalidBookCatalogQueryException(
                f"page_size cannot be greater than {_MAX_PAGE_SIZE}.",
                self.page_size,
            )
