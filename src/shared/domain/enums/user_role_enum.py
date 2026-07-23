"""This module contains the user role enum class."""

from enum import StrEnum


class UserRoleEnum(StrEnum):
    """Enumeration representing the different user roles in the system.

    This enumeration defines the possible roles that a user can have, which are:
    - `MEMBER`: a regular user with limited access to the library's services.
    - `LIBRARIAN`: an administrator with full access to the library's services.

    Attributes:
        MEMBER (str): The role for regular users.
        LIBRARIAN (str): The role for administrators.
    """

    MEMBER = "MEMBER"
    LIBRARIAN = "LIBRARIAN"
