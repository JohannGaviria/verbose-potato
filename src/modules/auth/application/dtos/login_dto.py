"""This module contains the login DTO."""

from dataclasses import dataclass
from uuid import UUID

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.access_token_result_vo import (
    AccessTokenResultVO,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum


@dataclass(frozen=True, slots=True)
class LoginCommandDto:
    """Command DTO for login use case class.

    Attributes:
        email (str): The user's email.
        password (str): The user's password.
    """

    email: str
    password: str


@dataclass(frozen=True, slots=True)
class UserLoginResponseDto:
    """Response DTO for login use case class.

    Attributes:
        id (UUID): The user's ID.
        name (str): The user's name.
        email (str): The user's email.
        role (UserRoleEnum): The user's role.
    """

    id: UUID
    name: str
    email: str
    role: UserRoleEnum

    @classmethod
    def response(cls, user: UserEntity) -> "UserLoginResponseDto":
        """Factory method to create a new instance of the response DTO.

        Args:
            user (UserEntity): The user entity to be transformed.

        Returns:
            UserLoginResponseDto: The new instance of the response DTO.
        """
        return cls(
            id=user.id,
            name=user.name.value,
            email=user.email.value,
            role=user.role,
        )


@dataclass(frozen=True, slots=True)
class AccessTokenResponseDto:
    """Response DTO for access token generation.

    Attributes:
        access_token (str): The access token.
        token_type (str): The type of token.
        expires_in (int): The number of seconds until the token expires.
    """

    access_token: str
    token_type: str
    expires_in: int

    @classmethod
    def response(
        cls, access_token_result: AccessTokenResultVO
    ) -> "AccessTokenResponseDto":
        """Factory method to create a new instance of the response DTO.

        Args:
            access_token_result (AccessTokenResultVO): The access token result to be transformed.

        Returns:
            AccessTokenResponseDto: The new instance of the response DTO.
        """
        return cls(
            access_token=access_token_result.access_token.value,
            token_type=access_token_result.token_type,
            expires_in=access_token_result.expires_in,
        )


@dataclass(frozen=True, slots=True)
class LoginResponseDto:
    """Response DTO for login use case class.

    Attributes:
        user (UserLoginResponseDto): The user's login response.
        access_token (AccessTokenResponseDto): The access token response.
    """

    user: UserLoginResponseDto
    access_token: AccessTokenResponseDto

    @classmethod
    def response(
        cls, user: UserEntity, access_token_result: AccessTokenResultVO
    ) -> "LoginResponseDto":
        """Factory method to create a new instance of the response DTO.

        Args:
            user (UserEntity): The user entity to be transformed.
            access_token_result (AccessTokenResultVO): The access token result to be transformed.

        Returns:
            LoginResponseDto: The new instance of the response DTO.
        """
        return cls(
            user=UserLoginResponseDto.response(user),
            access_token=AccessTokenResponseDto.response(access_token_result),
        )
