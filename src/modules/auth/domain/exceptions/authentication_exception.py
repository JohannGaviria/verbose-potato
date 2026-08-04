"""This module contains the authentication domain exceptions."""

from src.shared.domain.exceptions.base_domain_exception import BaseDomainException


class InvalidAccessTokenClaimsException(BaseDomainException):
    """Exception raised when invalid access token claims are provided."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidAccessTokenClaimsException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Invalid access token claims.")


class InvalidAccessTokenResultException(BaseDomainException):
    """Exception raised when invalid access token result is provided."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidAccessTokenResultException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Invalid access token result.")


class InvalidAccessTokenException(BaseDomainException):
    """Exception raised when invalid access token is provided."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidAccessTokenException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Invalid access token.")
