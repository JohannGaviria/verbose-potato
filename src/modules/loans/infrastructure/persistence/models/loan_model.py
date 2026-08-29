"""This module contains loan model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.models.base_model import BaseModel


class LoanModel(BaseModel):
    """SQLAlchemy model for loan.

    Attributes:
        id (Mapped[UUID]): Unique identifier of the loan.
        member_id: (Mapped[UUID]): Member id of the loan.
        book_id: (Mapped[UUID]): Book id of the loan.
        status (Mapped[str]): Status of the loan.
        loaned_at (Mapped[datetime]): Loaned at of the loan.
        returned_at (Mapped[datetime]): Returned at of the loan.
        created_at (Mapped[datetime]): Record creation date.
        updated_at (Mapped[datetime]): Date of the last update.
    """

    __tablename__ = "loans"

    member_id: Mapped[UUID] = mapped_column(nullable=True, index=True)
    book_id: Mapped[UUID] = mapped_column(nullable=True, index=True)
    status: Mapped[str] = mapped_column(nullable=True, index=True)
    loaned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    returned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
