from dataclasses import FrozenInstanceError

import pytest
from faker import Faker

from src.modules.books.domain.entities.book_entity import BookEntity
from src.modules.books.domain.exceptions.book_exception import (
    InvalidTotalCopiesException,
)
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

    def test_should_update_only_provided_fields_when_partial_data_is_given(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker)
        new_title = TitleVO(faker.sentence(nb_words=4))

        updated_book = book.update(title=new_title)

        assert updated_book.title == new_title
        assert updated_book.author == book.author
        assert updated_book.published_year == book.published_year
        assert updated_book.total_copies == book.total_copies

    def test_should_update_all_fields_when_full_data_is_given(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker, total_copies=TotalCopiesVO(5))

        new_title = TitleVO(faker.sentence(nb_words=4))
        new_author = AuthorVO(faker.name())
        new_published_year = PublishedYearVO(2015)
        new_total_copies = TotalCopiesVO(10)

        updated_book = book.update(
            title=new_title,
            author=new_author,
            published_year=new_published_year,
            total_copies=new_total_copies,
        )

        assert updated_book.title == new_title
        assert updated_book.author == new_author
        assert updated_book.published_year == new_published_year
        assert updated_book.total_copies == new_total_copies

    def test_should_keep_original_values_when_no_fields_are_provided(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker)

        updated_book = book.update()

        assert updated_book.title == book.title
        assert updated_book.author == book.author
        assert updated_book.published_year == book.published_year
        assert updated_book.total_copies == book.total_copies

    def test_should_keep_id_isbn_and_available_copies_unchanged_when_updated(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker, total_copies=TotalCopiesVO(5))

        updated_book = book.update(total_copies=TotalCopiesVO(10))

        assert updated_book.id == book.id
        assert updated_book.isbn == book.isbn
        assert updated_book.available_copies == book.available_copies

    def test_should_keep_created_at_unchanged_when_book_is_updated(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker)

        updated_book = book.update(title=TitleVO(faker.sentence(nb_words=4)))

        assert updated_book.created_at == book.created_at

    def test_should_refresh_updated_at_when_book_is_updated(self, faker: Faker) -> None:
        book = _build_book_entity(faker)

        updated_book = book.update(title=TitleVO(faker.sentence(nb_words=4)))

        assert updated_book.updated_at >= book.updated_at

    def test_should_return_new_instance_without_mutating_original_book(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker)
        original_title = book.title

        updated_book = book.update(title=TitleVO(faker.sentence(nb_words=4)))

        assert updated_book is not book
        assert book.title == original_title

    def test_should_raise_exception_when_total_copies_is_less_than_available_copies(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker, total_copies=TotalCopiesVO(5))

        with pytest.raises(InvalidTotalCopiesException):
            book.update(total_copies=TotalCopiesVO(book.available_copies - 1))

    def test_should_update_total_copies_when_equal_to_available_copies(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker, total_copies=TotalCopiesVO(5))

        updated_book = book.update(total_copies=TotalCopiesVO(book.available_copies))

        assert updated_book.total_copies.value == book.available_copies

    def test_should_update_total_copies_when_greater_than_available_copies(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker, total_copies=TotalCopiesVO(5))

        updated_book = book.update(
            total_copies=TotalCopiesVO(book.available_copies + 5)
        )

        assert updated_book.total_copies.value == book.available_copies + 5

    def test_should_return_false_when_available_copies_equal_total_copies(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker, total_copies=TotalCopiesVO(5))

        assert book.has_active_loans() is False

    def test_should_return_true_when_available_copies_are_less_than_total_copies(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker, total_copies=TotalCopiesVO(5))
        book_with_loan = BookEntity(
            id=book.id,
            title=book.title,
            isbn=book.isbn,
            author=book.author,
            published_year=book.published_year,
            total_copies=book.total_copies,
            available_copies=book.available_copies - 1,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )

        assert book_with_loan.has_active_loans() is True

    def test_should_return_true_when_all_copies_are_currently_on_loan(
        self, faker: Faker
    ) -> None:
        book = _build_book_entity(faker, total_copies=TotalCopiesVO(5))
        book_with_no_available_copies = BookEntity(
            id=book.id,
            title=book.title,
            isbn=book.isbn,
            author=book.author,
            published_year=book.published_year,
            total_copies=book.total_copies,
            available_copies=0,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )

        assert book_with_no_available_copies.has_active_loans() is True
