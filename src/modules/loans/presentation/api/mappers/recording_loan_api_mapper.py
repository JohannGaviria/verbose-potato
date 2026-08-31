"""This module contains the recording loan api mapper class."""

from src.modules.loans.application.dtos.recording_loan_dto import (
    RecordingLoanCommandDto,
    RecordingLoanResponseDto,
)
from src.modules.loans.presentation.api.schemas.recording_loan_schema import (
    RecordingLoanRequestSchema,
    RecordingLoanResponseSchema,
)


class RecordingLoanApiMapper:
    """Mapper class for recording loan API."""

    @staticmethod
    def to_command(
        request: RecordingLoanRequestSchema,
    ) -> RecordingLoanCommandDto:
        """Maps a recording loan request to a recording loan command DTO.

        Args:
            request (RecordingLoanRequestSchema): The recording loan request schema.

        Returns:
            RecordingLoanCommandDto: The recording loan command DTO.
        """
        return RecordingLoanCommandDto(
            book_id=request.book_id,
        )

    @staticmethod
    def to_response(
        response: RecordingLoanResponseDto,
    ) -> RecordingLoanResponseSchema:
        """Maps a recording loan response to a recording loan response schema.

        Args:
            response (RecordingLoanResponseDto): The recording loan response DTO.

        Returns:
            RecordingLoanResponseSchema: The recording loan response schema.
        """
        return RecordingLoanResponseSchema(
            id=response.id,
            member_id=response.member_id,
            book_id=response.book_id,
            status=response.status,
            loaned_at=response.loaned_at,
            returned_at=response.returned_at,
        )
