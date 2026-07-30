"""This module contains the domain exceptions for user credentials."""

from src.shared.domain.exceptions.base_exception import BaseException


class InvalidNameException(BaseException):
    """Exception raised when a name is invalid."""

    def __init__(self, error: str, name: str) -> None:
        """Initializes the InvalidNameException.

        Args:
            error (str): Error message describing name validation failures.
            name (str): Name that failed validation.
        """
        self.error = error
        self.name = name
        super().__init__("Invalid name provided.")


class InvalidEmailException(BaseException):
    """Exception raised when an email is invalid."""

    def __init__(self, error: str, email: str) -> None:
        """Initializes the InvalidEmailException.

        Args:
            error (str): Error message describing email validation failures.
            email (str): Email that failed validation.
        """
        self.error = error
        self.email = email
        super().__init__("Invalid email provided.")


class InvalidPasswordHashException(BaseException):
    """Exception raised when a password hash is invalid."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidPasswordHashException.

        Args:
            error (str): Error message describing password hash validation failures.
        """
        self.error = error
        super().__init__("Invalid password hash provided.")


class InvalidPlainPasswordException(BaseException):
    """Exception raised when a plain password is invalid."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidPlainPasswordException.

        Args:
            error (str): Error message describing plain password validation failures.
        """
        self.error = error
        super().__init__("Invalid plain password provided.")
