"""This module contains the authentication and authorization domain exceptions."""

from src.shared.domain.exceptions.base_domain_exception import BaseDomainException


class InvalidAccessTokenException(BaseDomainException):
    """Exception raised when invalid access token is provided."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidAccessTokenException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Invalid access token.")


class InvalidAccessTokenPayloadException(BaseDomainException):
    """Exception raised when invalid access token payload is provided."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidAccessTokenPayloadException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Invalid access token payload.")


class ExpiredAccessTokenException(BaseDomainException):
    """Exception raised when access token has expired."""

    def __init__(self) -> None:
        """Initializes the ExpiredAccessTokenException."""
        super().__init__("The access token has expired.")


class AuthenticationTokenMissingException(BaseDomainException):
    """Exception raised when authentication token is missing."""

    def __init__(self) -> None:
        """Initializes the AuthenticationTokenMissingException."""
        super().__init__("Authentication token is missing.")


class InsufficientPermissionsException(BaseDomainException):
    """Exception raised when user does not have sufficient permissions."""

    def __init__(self, error: str) -> None:
        """Initializes the InsufficientPermissionsException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Insufficient permissions.")
