"""This module contains the login schema."""

from uuid import UUID

from pydantic import BaseModel


class LoginRequestSchema(BaseModel):
    """Request schema for login.

    Attributes:
        email (str): The user's email.
        password (str): The user's password.
    """

    email: str
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePass!23",
            }
        }
    }


class UserLoginResponseSchema(BaseModel):
    """Response schema for login.

    Attributes:
        id (UUID): The user's ID.
        name (str): The user's name.
        email (str): The user's email.
        role (UserRoleEnum): The user's role.
    """

    id: UUID
    name: str
    email: str
    role: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "7e707d97-5896-4ad2-945d-f29e9e61ddc7",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "role": "MEMBER",
            }
        }
    }


class AccessTokenResponseSchema(BaseModel):
    """Response schema for access token generation.

    Attributes:
        access_token (str): The access token.
        token_type (str): The type of token.
        expires_in (int): The number of seconds until the token expires.
    """

    access_token: str
    token_type: str
    expires_in: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxNjgwMTI5YS1jMjUwLTQyYzUtYTE1MS01ZWJmODYzNDExOWMiLCJzdWIiOiJkOThmNjdlOS1kZWYxLTRhMjItOWM2Yy01ODFmMTQ5YWNhN2UiLCJyb2xlIjoiTElCUkFSSUFOIiwiZXhwIjoxNzg1ODg1MDA5fQ.3oAsgu9UingnuWNUsAP131V7ASR0-MyB-mBwU6jkqow",
                "token_type": "Bearer",
                "expires_in": 3600,
            }
        }
    }


class LoginResponseSchema(BaseModel):
    """Response schema for login.

    Attributes:
        user (UserLoginResponseSchema): The user's login response.
        access_token (AccessTokenResponseSchema): The access token response.
    """

    user: UserLoginResponseSchema
    access_token: AccessTokenResponseSchema

    model_config = {
        "json_schema_extra": {
            "example": {
                "user": {
                    "id": "7e707d97-5896-4ad2-945d-f29e9e61ddc7",
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "role": "MEMBER",
                },
                "access_token": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxNjgwMTI5YS1jMjUwLTQyYzUtYTE1MS01ZWJmODYzNDExOWMiLCJzdWIiOiJkOThmNjdlOS1kZWYxLTRhMjItOWM2Yy01ODFmMTQ5YWNhN2UiLCJyb2xlIjoiTElCUkFSSUFOIiwiZXhwIjoxNzg1ODg1MDA5fQ.3oAsgu9UingnuWNUsAP131V7ASR0-MyB-mBwU6jkqow",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
            }
        }
    }
