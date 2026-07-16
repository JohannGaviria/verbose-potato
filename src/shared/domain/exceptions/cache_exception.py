"""This module contains the cache exceptions class."""

from src.shared.domain.exceptions.base_exception import BaseException


class InvalidCacheKeyException(BaseException):
    """Exception raised when a cache key is invalid."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidCacheKeyException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Invalid cache key.")


class InvalidCacheTTLException(BaseException):
    """Exception raised when a cache TTL value is invalid."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidCacheTTLException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Invalid cache TTL.")


class InvalidCacheEntryException(BaseException):
    """Exception raised when a cache entry is invalid."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidCacheEntryException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Invalid cache entry.")


class CacheRetrievalException(BaseException):
    """Exception raised when there is an error retrieving data from the cache."""

    def __init__(self, error: str) -> None:
        """Initializes the CacheRetrievalException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Error retrieving data from cache.")


class CacheStorageException(BaseException):
    """Exception raised when there is an error storing data in the cache."""

    def __init__(self, error: str) -> None:
        """Initializes the CacheStorageException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Error storing data in cache.")


class CacheDeletionException(BaseException):
    """Exception raised when there is an error deleting data from the cache."""

    def __init__(self, error: str) -> None:
        """Initializes the CacheDeletionException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Error deleting data from cache.")
