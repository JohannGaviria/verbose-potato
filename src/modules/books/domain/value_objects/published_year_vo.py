"""This module contains the published year value object."""

from dataclasses import dataclass
from datetime import date

from src.modules.books.domain.exceptions.book_exception import (
    InvalidPublishedYearException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class PublishedYearVO(BaseValueObject):
    """Value object for representing a published year.

    Attributes:
        published_year (int): The published year.
    """

    published_year: int

    def _validate(self) -> None:
        """Validate the rules for the published year value object.

        The rules for the published year value object are:
        - Published year cannot be None.
        - Published year cannot be a boolean.
        - Published year must be an integer.
        - Published year must be between 1450 and the current year.

        Raises:
            InvalidPublishedYearException: If the published year does not
                meet the validation criteria.
        """
        if self.published_year is None:
            raise InvalidPublishedYearException(
                "Published year cannot be None.", self.published_year
            )
        if isinstance(self.published_year, bool):
            raise InvalidPublishedYearException(
                "Published year must be an integer.",
                self.published_year,
            )
        if not isinstance(self.published_year, int):
            raise InvalidPublishedYearException(
                "Published year must be an integer.",
                self.published_year,
            )

        current_year = date.today().year

        if self.published_year < 1450:
            raise InvalidPublishedYearException(
                "Published year cannot be earlier than 1450.",
                self.published_year,
            )
        if self.published_year > current_year:
            raise InvalidPublishedYearException(
                "Published year cannot be in the future.",
                self.published_year,
            )

    @property
    def value(self) -> int:
        """Return the published year as an integer.

        Returns:
            int: The published year value.
        """
        return self.published_year
