"""This module contains the title value object."""

from dataclasses import dataclass

from src.modules.books.domain.exceptions.book_exception import InvalidTitleException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class TitleVO(BaseValueObject):
    """Value object for representing a title.

    Attributes:
        title (str): The title.
    """

    title: str

    def _validate(self) -> None:
        """Validate the rules for the title value object.

        The rules for the title value object are:
        - Title cannot be None.
        - Title must be a string.
        - Title cannot be empty.
        - Title cannot be less than 3 characters.
        - Title cannot be longer than 255 characters.

        Raises:
            InvalidTitleException: If the title does not meet the validation criteria.
        """
        if self.title is None:
            raise InvalidTitleException("Title cannot be None.", self.title)
        if not isinstance(self.title, str):
            raise InvalidTitleException("Title must be a string.", self.title)
        if not self.title.strip():
            raise InvalidTitleException("Title cannot be empty.", self.title)
        if len(self.title) < 3:
            raise InvalidTitleException(
                "Title cannot be less than 3 characters.", self.title
            )
        if len(self.title) > 255:
            raise InvalidTitleException(
                "Title cannot be longer than 255 characters.", self.title
            )

    @property
    def value(self) -> str:
        """Return the title as a string.

        Returns:
            str: The title value.
        """
        return self.title
