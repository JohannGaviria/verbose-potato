"""This module contains the dtos for the get book catalog use case."""

from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Any
from uuid import UUID

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.enums.book_catalog_sort_by_enum import (
    BookCatalogSortByEnum,
)
from src.modules.books.domain.value_objects.book_catalog_cache_value_vo import (
    BookCatalogCacheValueVO,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum


@dataclass(frozen=True, slots=True)
class GetBookCatalogCommandDto:
    """Command DTO for the get book catalog use case.

    Attributes:
        title str: The title of the book catalog.
        author (str): The author of the book catalog.
        isbn (str): The ISBN of the book catalog.
        is_available (bool): Whether the book catalog is available.
        sort_by (BookCatalogSortByEnum): The sort by which book catalog is to be used.
        sort_order (SortOrderEnum): The sort order.
        page (int): The page of the book catalog.
        page_size (int): The page size of the book catalog.
    """

    title: str | None
    author: str | None
    isbn: str | None
    is_available: bool | None

    sort_by: BookCatalogSortByEnum | None
    sort_order: SortOrderEnum | None

    page: int
    page_size: int


@dataclass(frozen=True, slots=True)
class GetBookCatalogItemResponseDto:
    """Response dtos for a single book within the book catalog.

    Attributes:
        id (UUID): The book's id.
        title (str): The title of the book.
        isbn (str): The ISBN of the book.
        author (str): The author of the book.
        published_year (int): The year of publication of the book.
        total_copies (int): The total number of copies of the book.
        available_copies (int): The number of available copies of the book.
        created_at (datetime): The book's creation date.
        updated_at (datetime): The book's update date.
    """

    id: UUID
    title: str
    isbn: str
    author: str
    published_year: int
    total_copies: int
    available_copies: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: BookEntity) -> "GetBookCatalogItemResponseDto":
        """Build a book catalog item response dtos from a book entity.

        Args:
            entity (BookEntity): The book entity to convert.

        Returns:
            GetBookCatalogItemResponseDto: The book catalog item response dtos.
        """
        return cls(
            id=entity.id,
            title=entity.title.value,
            isbn=entity.isbn.value,
            author=entity.author.value,
            published_year=entity.published_year.value,
            total_copies=entity.total_copies.value,
            available_copies=entity.available_copies,
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
            "title": self.title,
            "isbn": self.isbn,
            "author": self.author,
            "published_year": self.published_year,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GetBookCatalogItemResponseDto":
        """Reconstruct a book catalog item response DTO from its dictionary representation.

        The dictionary is expected to contain the data read from the cache after
        JSON decoding.

        Args:
            data (dict[str, Any]): The raw cached item data.

        Returns:
            GetBookCatalogItemResponseDto: The rebuilt book catalog item
                response dtos.
        """
        return cls(
            id=UUID(str(data["id"])),
            title=data["title"],
            isbn=data["isbn"],
            author=data["author"],
            published_year=data["published_year"],
            total_copies=data["total_copies"],
            available_copies=data["available_copies"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


@dataclass(frozen=True, slots=True)
class GetBookCatalogResponseDto:
    """Response DTO for the get book catalog use case.

    Attributes:
       items (list[GetBookCatalogItemResponseDto]): The books for the current page.
       total (int): The total number of books matching the filters, ignoring pagination.
       page (int): The current page number.
       page_size (int): The number of items per page.
       total_pages (int): The total number of pages available.
    """

    items: list[GetBookCatalogItemResponseDto]
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0

    @classmethod
    def response(
        cls, books: list[BookEntity], total: int, page: int, page_size: int
    ) -> "GetBookCatalogResponseDto":
        """Response DTO for the get book catalog use case.

        Args:
            books (list[BookEntity]): The book entities for the current page.
            total (int): The total number of books matching the filters,
                ignoring pagination.
            page (int): The current page number.
            page_size (int): The number of items per page.
        """
        items = [GetBookCatalogItemResponseDto.from_entity(book) for book in books]
        total_pages = ceil(total / page_size) if page_size > 0 else 0

        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def to_cache_value(self) -> BookCatalogCacheValueVO:
        """Convert the response DTO into a book catalog cache value object.

        The resulting value object is used to store the catalog result in the cache.

        Returns:
            BookCatalogCacheValueVO: The cache value representing this paginated response.
        """
        return BookCatalogCacheValueVO(
            items=tuple(item.to_dict() for item in self.items),
            total=self.total,
            page=self.page,
            page_size=self.page_size,
            total_pages=self.total_pages,
        )

    @classmethod
    def from_cache_value(
        cls, cache_value: BookCatalogCacheValueVO
    ) -> "GetBookCatalogResponseDto":
        """Rebuild the paginated response dtos from a cached value (cache hit).

        Args:
            cache_value (BookCatalogCacheValueVO): The cached book catalog value.

        Returns:
            GetBookCatalogResponseDto: The paginated book catalog response dtos.
        """
        items = [
            GetBookCatalogItemResponseDto.from_dict(dict(item))
            for item in cache_value.items
        ]

        return cls(
            items=items,
            total=cache_value.total,
            page=cache_value.page,
            page_size=cache_value.page_size,
            total_pages=cache_value.total_pages,
        )
