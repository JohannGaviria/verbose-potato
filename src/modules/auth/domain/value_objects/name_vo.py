"""This module contains the name value object class."""

from dataclasses import dataclass

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidNameException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class NameVO(BaseValueObject):
    """Value object representing a name.

    Attributes:
        name (str): The name.
    """

    name: str

    def _validate(self) -> None:
        """Validates the rules for the name value object.

        The rules for the name value object are:
        - The name cannot be None.
        - The name must be a string.
        - The name cannot be empty.
        - The name cannot be less than 3 characters.
        - The name cannot be longer than 100 characters.

        Raises:
            InvalidNameException: If the name is invalid.
        """
        if self.name is None:
            raise InvalidNameException("Name be cannot None.", self.name)
        if not isinstance(self.name, str):
            raise InvalidNameException("Name must be a string.", self.name)
        if not self.name.strip():
            raise InvalidNameException("Name cannot be whitespace only.", self.name)
        if len(self.name) < 3:
            raise InvalidNameException(
                "Name cannot be less than 3 characters.", self.name
            )
        if len(self.name) > 100:
            raise InvalidNameException(
                "Name cannot be longer than 100 characters.", self.name
            )

    @property
    def value(self) -> str:
        """Returns the name as a string.

        Returns:
            str: The name.
        """
        return self.name
