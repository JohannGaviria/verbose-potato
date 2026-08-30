"""This module contains the loan persistence mapper."""

from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.infrastructure.persistence.models.loan_model import LoanModel


class LoanPersistenceMapper:
    """Mapper used to map loan entities to and from persistence models."""

    @staticmethod
    def to_model(entity: LoanEntity) -> LoanModel:
        """Maps a loan entity to a persistence model.

        Args:
            entity (LoanEntity): The loan entity to be mapped.

        Returns:
            LoanModel: The mapped loan model.
        """
        return LoanModel(
            id=entity.id,
            member_id=entity.member_id,
            book_id=entity.book_id,
            status=entity.status.value,
            loaned_at=entity.loaned_at,
            returned_at=entity.returned_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(model: LoanModel) -> LoanEntity:
        """Maps a persistence model to a loan entity.

        Args:
            model (LoanModel): The persistence model to be mapped.

        Returns:
            LoanEntity: The mapped loan entity.
        """
        return LoanEntity(
            id=model.id,
            member_id=model.member_id,
            book_id=model.book_id,
            status=LoanStatusEnum(model.status),
            loaned_at=model.loaned_at,
            returned_at=model.returned_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
