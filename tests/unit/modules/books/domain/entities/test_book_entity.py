from dataclasses import FrozenInstanceError

import pytest
from faker import Faker

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.value_objects.author_vo import AuthorVO
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO
from src.modules.books.domain.value_objects.published_year_vo import PublishedYearVO
from src.modules.books.domain.value_objects.title_vo import TitleVO
from src.modules.books.domain.value_objects.total_copies_vo import TotalCopiesVO

VALID_ISBN_13 = "9780306406157"


def _build_book_entity(
    faker: Faker,
    title: TitleVO | None = None,
    isbn: IsbnVO | None = None,
    author: AuthorVO | None = None,
    published_year: PublishedYearVO | None = None,
    total_copies: TotalCopiesVO | None = None,
) -> BookEntity:
    return BookEntity.create(
        title=title or TitleVO(faker.sentence(nb_words=4)),
        isbn=isbn or IsbnVO(VALID_ISBN_13),
        author=author or AuthorVO(faker.name()),
        published_year=published_year or PublishedYearVO(2020),
        total_copies=total_copies or TotalCopiesVO(5),
    )


class TestBookEntity:
    def test_should_create_book_entity_when_valid_data_is_provided(
        self, faker: Faker
    ) -> None:
        title = TitleVO(faker.sentence(nb_words=4))
        isbn = IsbnVO(VALID_ISBN_13)
        author = AuthorVO(faker.name())
        published_year = PublishedYearVO(2020)
        total_copies = TotalCopiesVO(5)

        book = BookEntity.create(
            title=title,
            isbn=isbn,
            author=author,
            published_year=published_year,
            total_copies=total_copies,
        )

        assert book.id is not None
        assert book.title == title
        assert book.isbn == isbn
        assert book.author == author
        assert book.published_year == published_year
        assert book.total_copies == total_copies
        assert book.created_at is not None
        assert book.updated_at is not None

    def test_should_set_available_copies_equal_to_total_copies_on_creation(
        self, faker: Faker
    ) -> None:
        total_copies = TotalCopiesVO(7)

        book = _build_book_entity(faker, total_copies=total_copies)

        assert book.available_copies == total_copies.value

    def test_should_set_created_at_and_updated_at_to_the_same_timestamp(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker)

        assert book.created_at == book.updated_at

    def test_should_return_correct_types_for_book_entity_attributes(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker)

        assert isinstance(book.title, TitleVO)
        assert isinstance(book.isbn, IsbnVO)
        assert isinstance(book.author, AuthorVO)
        assert isinstance(book.published_year, PublishedYearVO)
        assert isinstance(book.total_copies, TotalCopiesVO)
        assert isinstance(book.available_copies, int)

    def test_should_raise_exception_when_attempting_to_modify_book_entity_title(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker)

        with pytest.raises(FrozenInstanceError):
            book.title = TitleVO(faker.sentence(nb_words=4))  # type: ignore[misc]

    def test_should_return_equal_book_entities_when_data_is_identical(
        self, faker: Faker
    ) -> None:
        title = TitleVO(faker.sentence(nb_words=4))
        isbn = IsbnVO(VALID_ISBN_13)
        author = AuthorVO(faker.name())
        published_year = PublishedYearVO(2020)
        total_copies = TotalCopiesVO(5)

        book1 = BookEntity.create(title, isbn, author, published_year, total_copies)
        book2 = BookEntity(
            id=book1.id,
            title=title,
            isbn=isbn,
            author=author,
            published_year=published_year,
            total_copies=total_copies,
            available_copies=book1.available_copies,
            created_at=book1.created_at,
            updated_at=book1.updated_at,
        )

        assert book1 == book2

    def test_should_return_different_book_entities_when_ids_differ(
        self, faker: Faker
    ) -> None:
        book1 = _build_book_entity(faker)
        book2 = _build_book_entity(faker)

        assert book1 != book2
