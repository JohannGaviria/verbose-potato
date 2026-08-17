"""This module contains the book persistence mapper."""

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.value_objects.author_vo import AuthorVO
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.domain.value_objects.published_year_vo import PublishedYearVO
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.modules.books.domain.value_objects.total_copies_vo import TotalCopiesVO
from src.modules.books.infrastructure.persistence.models.book_model import BookModel


class BookPersistenceMapper:
    """Mapper used to map book entities to and from persistence models."""

    @staticmethod
    def to_model(entity: BookEntity) -> BookModel:
        """Maps a book entity to a persistence model.

        Args:
            entity (BookEntity): The book entity to be mapped.

        Returns:
            BookModel: The mapped book model.
        """
        return BookModel(
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

    @staticmethod
    def to_entity(model: BookModel) -> BookEntity:
        """Maps a persistence model to a book entity.

        Args:
            model (BookModel): The persistence model to be mapped.

        Returns:
            BookEntity: The mapped book entity.
        """
        return BookEntity(
            id=model.id,
            title=TitleVO(model.title),
            isbn=IsbnVO(model.isbn),
            author=AuthorVO(model.author),
            published_year=PublishedYearVO(model.published_year),
            total_copies=TotalCopiesVO(model.total_copies),
            available_copies=model.available_copies,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
