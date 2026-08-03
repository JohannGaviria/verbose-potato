"""This module contains the new user registration api mapper class."""

from src.modules.auth.application.dtos.new_user_registration_dto import (
    NewUserRegistrationCommandDto,
    NewUserRegistrationResponseDto,
)
from src.modules.auth.presentation.api.schemas.new_user_registration_schema import (
    NewUserRegistrationRequestSchema,
    NewUserRegistrationResponseSchema,
)


class NewUserRegistrationApiMapper:
    """Mapper class for new user registration API."""

    @staticmethod
    def to_command(
        request: NewUserRegistrationRequestSchema,
    ) -> NewUserRegistrationCommandDto:
        """Maps a new user registration request to a new user registration command DTO.

        Args:
            request (NewUserRegistrationRequestSchema): The new user registration request schema.

        Returns:
            NewUserRegistrationCommandDto: The new user registration command DTO.
        """
        return NewUserRegistrationCommandDto(
            name=request.name, email=request.email, password=request.password
        )

    @staticmethod
    def to_response(
        response: NewUserRegistrationResponseDto,
    ) -> NewUserRegistrationResponseSchema:
        """Maps a new user registration response to a new user registration response schema.

        Args:
            response (NewUserRegistrationResponseDto): The new user registration response DTO.

        Returns:
            NewUserRegistrationResponseSchema: The new user registration response schema.
        """
        return NewUserRegistrationResponseSchema(
            id=response.id,
            name=response.name,
            email=response.email,
            role=response.role,
            created_at=response.created_at,
            updated_at=response.updated_at,
        )
