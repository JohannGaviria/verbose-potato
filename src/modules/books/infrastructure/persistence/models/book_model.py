"""This module contains the book model."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.models.base_model import BaseModel


class BookModel(BaseModel):
    """SQLAlchemy model class for books.

    Attributes:
        id (Mapped[UUID]): Unique identifier of the book.
        title (Mapped[str]): Title of the book.
        isbn (Mapped[str]): ISBN code of the book.
        author (Mapped[str]): Author of the book.
        published_year (Mapped[int]): Year of publication.
        total_copies (Mapped[int]): Total number of registered copies.
        available_copies (Mapped[int]): Number of copies currently available.
        created_at (Mapped[datetime]): Record creation date.
        updated_at (Mapped[datetime]): Date of the last update.
    """

    __tablename__ = "books"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    isbn: Mapped[str] = mapped_column(
        String(13), nullable=False, unique=True, index=True
    )
    author: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    published_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    total_copies: Mapped[int] = mapped_column(Integer, nullable=False)
    available_copies: Mapped[int] = mapped_column(Integer, nullable=False)
