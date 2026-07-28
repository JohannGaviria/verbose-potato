"""This module contains the user domain exceptions."""

from src.shared.domain.exceptions.base_exception import BaseException


class LibrarianAlreadyExistsException(BaseException):
    """Exception raised when a librarian already exists."""

    def __init__(self) -> None:
        """Initializes the LibrarianAlreadyExistsException."""
        super().__init__("A librarian user is already registered.")


class UserRepositoryException(BaseException):
    """Exception raised when an error occurs while interacting with the user repository."""

    def __init__(self, error: str) -> None:
        """Initializes the UserRepositoryException.

        Args:
            error (str): The error message.
        """
        super().__init__("Error while interacting with the user repository.")
