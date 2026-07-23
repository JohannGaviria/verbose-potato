"""This module contains the user domain exceptions."""

from src.shared.domain.exceptions.base_exception import BaseException


class LibrarianAlreadyExistsException(BaseException):
    """Exception raised when a librarian already exists."""

    def __init__(self) -> None:
        """Initializes the LibrarianAlreadyExistsException."""
        super().__init__("A librarian user is already registered.")
