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
