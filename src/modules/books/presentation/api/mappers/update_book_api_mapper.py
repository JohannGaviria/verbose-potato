"""This module contains the update book api mapper class."""

from uuid import UUID

from src.modules.books.application.dtos.update_book_dto import (
    UpdateBookCommandDto,
    UpdateBookResponseDto,
)
from src.modules.books.presentation.api.schemas.update_book_schema import (
    UpdateBookRequestSchema,
    UpdateBookResponseSchema,
)


class UpdateBookApiMapper:
    """Mapper class for update book API."""

    @staticmethod
    def to_command(
        book_id: UUID,
        request: UpdateBookRequestSchema,
    ) -> UpdateBookCommandDto:
        """Maps an update book request to an update book command DTO.

        Args:
            book_id (UUID): The ID of the book to be updated.
            request (UpdateBookRequestSchema): The update book request schema.

        Returns:
            UpdateBookCommandDto: The update book command DTO.
        """
        return UpdateBookCommandDto(
            book_id=book_id,
            title=request.title,
            author=request.author,
            published_year=request.published_year,
            total_copies=request.total_copies,
        )

    @staticmethod
    def to_response(
        response: UpdateBookResponseDto,
    ) -> UpdateBookResponseSchema:
        """Maps an update book response to an update book response schema.

        Args:
            response (UpdateBookResponseDto): The update book response DTO.

        Returns:
            UpdateBookResponseSchema: The update book response schema.
        """
        return UpdateBookResponseSchema(
            id=response.id,
            title=response.title,
            isbn=response.isbn,
            author=response.author,
            published_year=response.published_year,
            total_copies=response.total_copies,
            available_copies=response.available_copies,
            created_at=response.created_at,
            updated_at=response.updated_at,
        )
