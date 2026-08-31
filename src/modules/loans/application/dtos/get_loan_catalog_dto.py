"""This module contains the dtos for the get loan catalog use case."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Any
from uuid import UUID

from src.modules.loans.domain.entities.loan_entity import LoanEntity
from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.value_objects.loan_catalog_cache_value_vo import (
    LoanCatalogCacheValueVO,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum


@dataclass(frozen=True, slots=True)
class GetLoanCatalogCommandDto:
    """Data Transfer Object for the get loan catalog command.

    Attributes:
        member_id (UUID | None): Optional member filter.
        book_id (UUID | None): Optional book filter.
        status (LoanStatusEnum | None): Optional loan status filter.
        sort_by (LoanSortByEnum | None): Field used to sort the loans.
        sort_order (SortOrderEnum | None): Sort direction.
        page (int): The requested page number.
        page_size (int): The number of items per page.
    """

    member_id: UUID | None
    book_id: UUID | None
    status: LoanStatusEnum | None
    sort_by: LoanSortByEnum | None
    sort_order: SortOrderEnum | None
    page: int
    page_size: int


@dataclass(frozen=True, slots=True)
class GetLoanCatalogItemResponseDto:
    """Data Transfer Object for a get loan catalog item response.

    Attributes:
        id (UUID): Unique identifier of the loan.
        member_id (UUID): Unique identifier of the member of the loan.
        book_id (UUID): Unique identifier of the book of the loan.
        status (LoanStatusEnum): Status of the loan.
        loaned_at (datetime): Date and time at which the loan was loaned.
        returned_at (datetime | None): Date and time at which the loan was returned.
        created_at (datetime): Date and time at which the loan was created.
        updated_at (datetime): Date and time at which the loan was last updated.
    """

    id: UUID
    member_id: UUID
    book_id: UUID
    status: LoanStatusEnum
    loaned_at: datetime
    returned_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: LoanEntity) -> "GetLoanCatalogItemResponseDto":
        """Build a get loan catalog item response from a loan entity.

        Args:
            entity (LoanEntity): The loan entity to convert.

        Returns:
            GetLoanCatalogItemResponseDto: The get loan catalog item response.
        """
        return cls(
            id=entity.id,
            member_id=entity.member_id,
            book_id=entity.book_id,
            status=entity.status,
            loaned_at=entity.loaned_at,
            returned_at=entity.returned_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the item to a JSON-serializable dictionary, used to build the cache value.

        Returns:
            dict[str, Any]: The dictionary representation of the item.
        """
        return {
            "id": str(self.id),
            "member_id": str(self.member_id),
            "book_id": str(self.book_id),
            "status": self.status.value,
            "loaned_at": self.loaned_at.isoformat(),
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GetLoanCatalogItemResponseDto":
        """Reconstruct a get loan catalog item response DTO from its dictionary representation.

        The dictionary is expected to contain the data read from the cache after
        JSON decoding.

        Args:
            data (Mapping[str, Any]): The raw cached item data.

        Returns:
            GetLoanCatalogItemResponseDto: The rebuilt item response.
        """
        returned_at = data.get("returned_at")
        return cls(
            id=UUID(str(data["id"])),
            member_id=UUID(str(data["member_id"])),
            book_id=UUID(str(data["book_id"])),
            status=LoanStatusEnum(data["status"]),
            loaned_at=datetime.fromisoformat(data["loaned_at"]),
            returned_at=(datetime.fromisoformat(returned_at) if returned_at else None),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


@dataclass(frozen=True, slots=True)
class GetLoanCatalogResponseDto:
    """Data Transfer Object for the get loan catalog response.

    Attributes:
        items (list[GetLoanCatalogItemResponseDto]): The list of loans.
        total (int): Total number of matching loans.
        page (int): The requested page number.
        page_size (int): The number of items per page.
        total_pages (int): Total number of pages.
    """

    items: list[GetLoanCatalogItemResponseDto]
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0

    @classmethod
    def response(
        cls,
        loans: list[LoanEntity],
        total: int,
        page: int,
        page_size: int,
    ) -> "GetLoanCatalogResponseDto":
        """Build a get loan catalog response from a list of loan entities.

        Args:
            loans (list[LoanEntity]): The loan entities to convert.
            total (int): Total number of matching loans.
            page (int): The requested page number.
            page_size (int): The number of items per page.

        Returns:
            GetLoanCatalogResponseDto: The get loan catalog response.
        """
        items = [GetLoanCatalogItemResponseDto.from_entity(loan) for loan in loans]
        total_pages = ceil(total / page_size) if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def to_cache_value(self) -> LoanCatalogCacheValueVO:
        """Convert the response to a cache value.

        Returns:
            LoanCatalogCacheValueVO: The cache value representation of the response.
        """
        return LoanCatalogCacheValueVO(
            items=tuple(item.to_dict() for item in self.items),
            total=self.total,
            page=self.page,
            page_size=self.page_size,
            total_pages=self.total_pages,
        )

    @classmethod
    def from_cache_value(
        cls, cache_value: LoanCatalogCacheValueVO
    ) -> "GetLoanCatalogResponseDto":
        """Reconstruct the response from a cache value.

        Args:
            cache_value (LoanCatalogCacheValueVO): The cache value read.

        Returns:
            GetLoanCatalogResponseDto: The rebuilt get loan catalog response.
        """
        items = [
            GetLoanCatalogItemResponseDto.from_dict(dict(item))
            for item in cache_value.items
        ]
        return cls(
            items=items,
            total=cache_value.total,
            page=cache_value.page,
            page_size=cache_value.page_size,
            total_pages=cache_value.total_pages,
        )
