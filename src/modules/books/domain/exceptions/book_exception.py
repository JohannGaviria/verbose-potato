"""This module contains the book domain exceptions."""

from src.shared.domain.exceptions.base_domain_exception import BaseDomainException


class InvalidTitleException(BaseDomainException):
    """Exception raised when the title is invalid."""

    def __init__(self, error: str, title: str) -> None:
        """Initialize the InvalidTitleException.

        Args:
            error (str): The error message.
            title (str): the invalid title.
        """
        self.error = error
        self.title = title
        super().__init__("Invalid title provided.")


class InvalidAuthorException(BaseDomainException):
    """Exception raised when the author is invalid."""

    def __init__(self, error: str, author: str) -> None:
        """Initialize the InvalidAuthorException.

        Args:
            error (str): The error message.
            author (str): the invalid author.
        """
        self.error = error
        self.author = author
        super().__init__("Invalid author provided.")


class InvalidPublishedYearException(BaseDomainException):
    """Exception raised when the published year is invalid."""

    def __init__(self, error: str, published_year: int) -> None:
        """Initialize the InvalidPublishedYearException.

        Args:
            error (str): The error message.
            published_year (int): the invalid published year.
        """
        self.error = error
        self.published_year = published_year
        super().__init__("Invalid published year provided.")


class InvalidTotalCopiesException(BaseDomainException):
    """Exception raised when the total copies is invalid."""

    def __init__(self, error: str, total_copies: int) -> None:
        """Initialize the InvalidTotalCopiesException.

        Args:
            error (str): The error message.
            total_copies (int): the invalid total copies.
        """
        self.error = error
        self.total_copies = total_copies
        super().__init__("Invalid total copies provided.")


class InvalidIsbnException(BaseDomainException):
    """Exception raised when the isbn is invalid."""

    def __init__(self, error: str, isbn: str) -> None:
        """Initialize the InvalidIsbnException.

        Args:
            error (str): The error message.
            isbn (str): the invalid isbn.
        """
        self.error = error
        self.isbn = isbn
        super().__init__("Invalid isbn provided.")


class ISBNAlreadyRegisteredException(BaseDomainException):
    """Exception raised when the isbn is already registered."""

    def __init__(self) -> None:
        """Initialize the ISBNAlreadyRegisteredException."""
        super().__init__("ISBN already registered.")


class InvalidBookCatalogQueryException(BaseDomainException):
    """Exception raised when the book catalog query is invalid."""

    def __init__(self, error: str, query: str | int) -> None:
        """Initialize the InvalidBookCatalogQueryException.

        Args:
            error (str): The error message.
            query (str): the invalid book catalog.
        """
        self.error = error
        self.query = query
        super().__init__("Invalid book catalog query provided.")
