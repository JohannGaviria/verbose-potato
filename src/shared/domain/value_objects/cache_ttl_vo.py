"""This module contains the cache ttl vo class."""

from dataclasses import dataclass

from src.shared.domain.exceptions.cache_exception import InvalidCacheTTLException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class CacheTTLVO(BaseValueObject):
    """Value object for cache time to live (TTL).

    Attributes:
        seconds (int): The time to live in seconds.
    """

    seconds: int

    def _validate(self) -> None:
        """Validate the value object.

        Raises:
            InvalidCacheTTLException: If the value object is invalid.
        """
        if self.seconds is None:
            raise InvalidCacheTTLException("seconds cannot be empty.")
        if not isinstance(self.seconds, int):
            raise InvalidCacheTTLException("seconds must be an integer.")
        if self.seconds < 0:
            raise InvalidCacheTTLException("seconds must be positive.")
        if self.seconds > 2592000:
            raise InvalidCacheTTLException("seconds to long (max 30 days).")

    def value(self) -> int:
        """Return the value of the cache TTL.

        Returns:
            int: The value of the cache TTL.
        """
        return self.seconds
