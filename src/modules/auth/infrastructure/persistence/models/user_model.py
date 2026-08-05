"""This module contains the user model class."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.models.base_model import BaseModel


class UserModel(BaseModel):
    """SQLAlchemy model class for users.

    Attributes:
        id (Mapped[UUID]): Unique identifier of the user.
        name (Mapped[str]): Full name of the user.
        email (Mapped[str]): User's email address.
        password (Mapped[str]): Password hashed using Argon2.
        role (Mapped[str]): User's role within the system.
        created_at (Mapped[datetime]): Record creation date.
        updated_at (Mapped[datetime]): Date of the last update.
    """

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(nullable=False, index=True)
