"""This module contains the dtos for the delete book use case."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DeleteBookCommandDto:
    """Command dtos for the delete book use case.

    Attributes:
        book_id (UUID): The ID of the book to delete.
    """

    book_id: UUID
