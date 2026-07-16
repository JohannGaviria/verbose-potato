"""This module contains the base value object class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BaseValueObject(ABC):
    """Base class for value objects."""

    def __post_init__(self) -> None:
        """After the dataclass is initialized.

        this method is called to perform validation on the value object.
        If the validation fails, it should raise an exception.
        """
        self._validate()

    @abstractmethod
    def _validate(self) -> None:
        """Validate the value object.

        This method should be implemented by subclasses to perform validation on the value object.
        If the validation fails, it should raise an exception.
        """
        pass
