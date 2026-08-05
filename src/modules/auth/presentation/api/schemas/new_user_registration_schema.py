"""This module contains the new user registration schema."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.shared.domain.enums.user_role_enum import UserRoleEnum


class NewUserRegistrationRequestSchema(BaseModel):
    """Request schema for new user registration.

    Attributes:
        name (str): The user's name.
        email (str): The user's email.
        password (str): The user's password.
    """

    name: str
    email: str
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "SecurePass!23",
            }
        }
    }


class NewUserRegistrationResponseSchema(BaseModel):
    """Response schema for new user registration.

    Attributes:
        id (UUID): The user's id.
        name (str): The user's name.
        email (str): The user's email.
        role (UserRoleEnum): The user's role.
        created_at (datetime): The user's creation date.
        updated_at (datetime): The user's update date.
    """

    id: UUID
    name: str
    email: str
    role: UserRoleEnum
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "7e707d97-5896-4ad2-945d-f29e9e61ddc7",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "role": "MEMBER",
                "created_at": "2026-08-03 18:59:40.152699+00:00",
                "updated_at": "2026-08-03 18:59:40.152699+00:00",
            }
        }
    }
