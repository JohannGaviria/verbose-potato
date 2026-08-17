"""This module contains the registration new book api mapper class."""

from src.modules.books.application.dtos.registration_new_book_dto import (
    RegistrationNewBookCommandDto,
    RegistrationNewBookResponseDto,
)
from src.modules.books.presentation.api.schemas.registration_new_book_schema import (
    RegistrationNewBookRequestSchema,
    RegistrationNewBookResponseSchema,
)


class RegistrationNewBookApiMapper:
    """Mapper class for registration new book API."""

    @staticmethod
    def to_command(
        request: RegistrationNewBookRequestSchema,
    ) -> RegistrationNewBookCommandDto:
        """Maps a registration new book request to a registration new book command DTO.

        Args:
            request (RegistrationNewBookRequestSchema): The registration new book request schema.

        Returns:
            RegistrationNewBookCommandDto: The registration new book command DTO.
        """
        return RegistrationNewBookCommandDto(
            title=request.title,
            isbn=request.isbn,
            author=request.author,
            published_year=request.published_year,
            total_copies=request.total_copies,
        )

    @staticmethod
    def to_response(
        response: RegistrationNewBookResponseDto,
    ) -> RegistrationNewBookResponseSchema:
        """Maps a registration new book response to a registration new book response schema.

        Args:
            response (RegistrationNewBookResponseDto): The registration new book response DTO.

        Returns:
            RegistrationNewBookResponseSchema: The registration new book response schema.
        """
        return RegistrationNewBookResponseSchema(
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
