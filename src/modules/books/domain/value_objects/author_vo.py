"""This module contains the author value object."""

from dataclasses import dataclass

from src.modules.books.domain.exceptions.book_exception import InvalidAuthorException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class AuthorVO(BaseValueObject):
    """Value object for representing an author.

    Attributes:
        author (str): The author name.
    """

    author: str

    def _validate(self) -> None:
        """Validate the rules for the author value object.

        The rules for the author value object are:
        - Author cannot be None.
        - Author must be a string.
        - Author cannot be empty.
        - Author cannot be less than 3 characters.
        - Author cannot be longer than 100 characters.

        Raises:
            InvalidAuthorException: If the author does not meet the validation criteria.
        """
        if self.author is None:
            raise InvalidAuthorException("Author cannot be None.", self.author)
        if not isinstance(self.author, str):
            raise InvalidAuthorException("Author must be a string.", self.author)
        if not self.author.strip():
            raise InvalidAuthorException("Author cannot be empty string.", self.author)
        if len(self.author) < 3:
            raise InvalidAuthorException(
                "Author cannot be less than 3 characters.", self.author
            )
        if len(self.author) > 100:
            raise InvalidAuthorException(
                "Author cannot be longer than 100 characters.", self.author
            )

    @property
    def value(self) -> str:
        """Return the author as a string.

        Returns:
            str: The author value.
        """
        return self.author
