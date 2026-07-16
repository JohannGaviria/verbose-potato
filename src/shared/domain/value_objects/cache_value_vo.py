"""This module contains the cache value vo class."""

from abc import abstractmethod
from dataclasses import dataclass

from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class CacheValueVO(BaseValueObject):
    """Value object for cache value."""

    def _validate(self) -> None:
        """Validate the cache value."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the cache value to a dictionary.

        Returns:
            dict: The dictionary representation of the cache value.
        """
        pass
