"""This module contains the dtos for create first librarian use case class."""

from dataclasses import dataclass

from src.modules.auth.application.dtos.base_auth_dto import BaseUserDto


@dataclass(frozen=True, slots=True)
class CreateFirstLibrarianCommandDto(BaseUserDto):
    """Command DTO for creating the first librarian user.

    Attributes:
        name (str): The user's name.
        email (str): The user's email.
        password (str): The user's password.
    """

    ...
