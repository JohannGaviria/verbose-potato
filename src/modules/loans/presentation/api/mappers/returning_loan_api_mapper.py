"""This module contains the returning loan api mapper class."""

from uuid import UUID

from src.modules.loans.application.dtos.returning_loan_dto import (
    ReturningLoanCommandDto,
    ReturningLoanResponseDto,
)
from src.modules.loans.presentation.api.schemas.returning_loan_schema import (
    ReturningLoanResponseSchema,
)


class ReturningLoanApiMapper:
    """Mapper class for returning loan API."""

    @staticmethod
    def to_command(loan_id: UUID) -> ReturningLoanCommandDto:
        """Maps a loan id to a returning loan command DTO.

        Args:
            loan_id (UUID): The loan id to return.

        Returns:
            ReturningLoanCommandDto: The returning loan command DTO.
        """
        return ReturningLoanCommandDto(
            loan_id=loan_id,
        )

    @staticmethod
    def to_response(
        response: ReturningLoanResponseDto,
    ) -> ReturningLoanResponseSchema:
        """Maps a returning loan response to a returning loan response schema.

        Args:
            response (ReturningLoanResponseDto): The returning loan response DTO.

        Returns:
            ReturningLoanResponseSchema: The returning loan response schema.
        """
        return ReturningLoanResponseSchema(
            id=response.id,
            member_id=response.member_id,
            book_id=response.book_id,
            status=response.status,
            loaned_at=response.loaned_at,
            returned_at=response.returned_at,
        )
