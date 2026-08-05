"""This module contains the base entity class."""

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class BaseEntity(ABC):
    """BaseEntity is a base class for entities in the domain layer.

    Attributes:
        id (UUID): The unique identifier of the entity.
        created_at (datetime): The date and time when the entity was created.
        updated_at (datetime): The date and time when the entity was last updated.
    """

    id: UUID
    created_at: datetime
    updated_at: datetime

    def __eq__(self, other: object) -> bool:
        """Check if two entities are equal based on their ID.

        Args:
            other (object): The other entity to compare with.

        Returns:
            bool: True if the entities are equal, False otherwise.
        """
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id
