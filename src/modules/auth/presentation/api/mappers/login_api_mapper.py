"""This module contains the login api mapper."""

from src.modules.auth.application.dtos.login_dto import (
    AccessTokenResponseDto,
    LoginCommandDto,
    LoginResponseDto,
    UserLoginResponseDto,
)
from src.modules.auth.presentation.api.schemas.login_schema import (
    AccessTokenResponseSchema,
    LoginRequestSchema,
    LoginResponseSchema,
    UserLoginResponseSchema,
)


class LoginApiMapper:
    """Mapper class for login API."""

    @staticmethod
    def to_command(
        request: LoginRequestSchema,
    ) -> LoginCommandDto:
        """Maps a login request to a login command DTO.

        Args:
            request (LoginRequestSchema): The login request schema.

        Returns:
            LoginCommandDto: The login command DTO.
        """
        return LoginCommandDto(
            email=request.email,
            password=request.password,
        )

    @staticmethod
    def _to_user_login_response(
        response: UserLoginResponseDto,
    ) -> UserLoginResponseSchema:
        """Maps a user login response to a user login response schema.

        Args:
            response (UserLoginResponseDto): The user login response DTO.

        Returns:
            UserLoginResponseSchema: The user login response schema.
        """
        return UserLoginResponseSchema(
            id=response.id,
            name=response.name,
            email=response.email,
            role=response.role,
        )

    @staticmethod
    def _to_access_token_response(
        response: AccessTokenResponseDto,
    ) -> AccessTokenResponseSchema:
        """Maps an access token response to an access token response schema.

        Args:
            response (AccessTokenResponseDto): The access token response DTO.

        Returns:
            AccessTokenResponseSchema: The access token response schema.
        """
        return AccessTokenResponseSchema(
            access_token=response.access_token,
            token_type=response.token_type,
            expires_in=response.expires_in,
        )

    @staticmethod
    def to_response(
        response: LoginResponseDto,
    ) -> LoginResponseSchema:
        """Maps a login response to a login response schema.

        Args:
            response (LoginResponseDto): The login response DTO.

        Returns:
            LoginResponseSchema: The login response schema.
        """
        return LoginResponseSchema(
            user=LoginApiMapper._to_user_login_response(response.user),
            access_token=LoginApiMapper._to_access_token_response(
                response.access_token
            ),
        )
