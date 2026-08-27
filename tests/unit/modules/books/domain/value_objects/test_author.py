from dataclasses import FrozenInstanceError
from typing import Any

import pytest
from faker import Faker

from src.modules.books.domain.exceptions.book_exception import InvalidAuthorException
from src.modules.books.domain.value_objects.author_vo import AuthorVO


class TestAuthorVO:
    def test_should_return_author_as_string_when_valid_author_is_provided(
        self, faker: Faker
    ) -> None:
        author = faker.name()
        author_vo = AuthorVO(author)

        assert author_vo.value == author

    def test_should_raise_exception_when_author_is_none(self) -> None:
        with pytest.raises(InvalidAuthorException):
            AuthorVO(None)  # type: ignore[arg-type]

    def test_should_raise_exception_when_author_is_empty(self) -> None:
        with pytest.raises(InvalidAuthorException):
            AuthorVO("")

    @pytest.mark.parametrize("author", [123, True, False, [], {}])
    def test_should_raise_exception_when_author_is_not_a_string(
        self, author: Any
    ) -> None:
        with pytest.raises(InvalidAuthorException):
            AuthorVO(author)

    @pytest.mark.parametrize(
        "author",
        [
            "",
            " ",
            "   ",
            "\t",
            "\n",
            "\r\n",
        ],
    )
    def test_should_raise_exception_when_author_is_whitespace_only(
        self, author: str
    ) -> None:
        with pytest.raises(InvalidAuthorException):
            AuthorVO(author)

    @pytest.mark.parametrize(
        "author",
        [
            "a",
            "ab",
        ],
    )
    def test_should_raise_exception_when_author_is_too_short(self, author: str) -> None:
        with pytest.raises(InvalidAuthorException):
            AuthorVO(author)

    def test_should_raise_exception_when_author_exceeds_max_length(self) -> None:
        with pytest.raises(InvalidAuthorException):
            AuthorVO("a" * 101)

    def test_should_not_raise_exception_when_author_is_at_min_length(self) -> None:
        author_vo = AuthorVO("abc")

        assert author_vo.value == "abc"

    def test_should_not_raise_exception_when_author_is_at_max_length(self) -> None:
        author = "a" * 100
        author_vo = AuthorVO(author)

        assert author_vo.value == author

    def test_should_raise_exception_when_attempting_to_modify_author(
        self, faker: Faker
    ) -> None:
        author_vo = AuthorVO(faker.name())

        with pytest.raises(FrozenInstanceError):
            author_vo.author = faker.name()  # type: ignore[misc]
