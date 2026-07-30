"""This module contains the base authentication DTO class."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BaseUserDto:
    """Base DTO for user's.

    Attributes:
        name (str): The user's name.
        email (str): The user's email.
        password (str): The user's password.
    """

    name: str
    email: str
    password: str
