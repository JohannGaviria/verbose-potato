"""This module contains the dtos for create first librarian use case class."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateFirstLibrarianCommandDto:
    """Command DTO for creating the first librarian user.

    Attributes:
        name (str): The user's name.
        email (str): The user's email.
        password (str): The user's password.
    """

    name: str
    email: str
    password: str
