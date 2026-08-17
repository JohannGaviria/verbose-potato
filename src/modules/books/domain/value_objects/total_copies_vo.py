"""This module contains the total copies value object."""

from dataclasses import dataclass

from src.modules.books.domain.exceptions.book_exception import (
    InvalidTotalCopiesException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class TotalCopiesVO(BaseValueObject):
    """Value object for representing the total copies of a book.

    Attributes:
        total_copies (int): The total number of copies.
    """

    total_copies: int

    def _validate(self) -> None:
        """Validate the rules for the total copies value object.

        The rules for the total copies value object are:
        - Total copies cannot be None.
        - Total copies cannot be a boolean.
        - Total copies must be an integer.
        - Total copies must be greater than or equal to 1.

        Raises:
            InvalidTotalCopiesException: If the total copies do not
                meet the validation criteria.
        """
        if self.total_copies is None:
            raise InvalidTotalCopiesException(
                "Total copies cannot be None.", self.total_copies
            )
        if isinstance(self.total_copies, bool):
            raise InvalidTotalCopiesException(
                "Total copies must be an integer.",
                self.total_copies,
            )
        if not isinstance(self.total_copies, int):
            raise InvalidTotalCopiesException(
                "Total copies must be an integer.",
                self.total_copies,
            )
        if self.total_copies < 1:
            raise InvalidTotalCopiesException(
                "Total copies must be greater than or equal to 1.",
                self.total_copies,
            )

    @property
    def value(self) -> int:
        """Return the total copies as an integer.

        Returns:
            int: The total copies value.
        """
        return self.total_copies
