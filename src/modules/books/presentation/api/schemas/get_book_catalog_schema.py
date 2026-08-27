"""This module contains the get book catalog schema."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GetBookCatalogItemResponseSchema(BaseModel):
    """Response schema for a single book within the book catalog.

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

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "7e707d97-5896-4ad2-945d-f29e9e61ddc7",
                "title": "Clean Architecture",
                "isbn": "9780134494166",
                "author": "Robert C. Martin",
                "published_year": 2017,
                "total_copies": 5,
                "available_copies": 5,
                "created_at": "2026-08-03 18:59:40.152699+00:00",
                "updated_at": "2026-08-03 18:59:40.152699+00:00",
            }
        }
    }


class GetBookCatalogResponseSchema(BaseModel):
    """Response schema for the paginated book catalog.

    Attributes:
        items (list[GetBookCatalogItemResponseSchema]): The books for the current page.
        total (int): The total number of books matching the filters, ignoring pagination.
        page (int): The current page number.
        page_size (int): The number of items per page.
        total_pages (int): The total number of pages available.
    """

    items: list[GetBookCatalogItemResponseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": "7e707d97-5896-4ad2-945d-f29e9e61ddc7",
                        "title": "Clean Architecture",
                        "isbn": "9780134494166",
                        "author": "Robert C. Martin",
                        "published_year": 2017,
                        "total_copies": 5,
                        "available_copies": 5,
                        "created_at": "2026-08-03 18:59:40.152699+00:00",
                        "updated_at": "2026-08-03 18:59:40.152699+00:00",
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 20,
                "total_pages": 1,
            }
        }
    }
