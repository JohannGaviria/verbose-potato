from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from src.modules.books.domain.exceptions.book_exception import InvalidIsbnException
from src.modules.books.domain.value_objects.isbn_vo import IsbnVO

VALID_ISBN_10 = "0136091814"
VALID_ISBN_10_WITH_X_CHECK_DIGIT = "317066907X"
VALID_ISBN_13 = "9780306406157"


class TestIsbnVO:
    def test_should_return_isbn_as_string_when_valid_isbn_10_is_provided(
        self,
    ) -> None:
        isbn_vo = IsbnVO(VALID_ISBN_10)

        assert isbn_vo.value == VALID_ISBN_10

    def test_should_accept_isbn_10_with_x_check_digit(self) -> None:
        isbn_vo = IsbnVO(VALID_ISBN_10_WITH_X_CHECK_DIGIT)

        assert isbn_vo.value == VALID_ISBN_10_WITH_X_CHECK_DIGIT

    def test_should_return_isbn_as_string_when_valid_isbn_13_is_provided(
        self,
    ) -> None:
        isbn_vo = IsbnVO(VALID_ISBN_13)

        assert isbn_vo.value == VALID_ISBN_13

    def test_should_accept_isbn_10_with_hyphens(self) -> None:
        hyphenated = f"{VALID_ISBN_10[0]}-{VALID_ISBN_10[1:4]}-{VALID_ISBN_10[4:9]}-{VALID_ISBN_10[9]}"
        isbn_vo = IsbnVO(hyphenated)

        assert isbn_vo.value == hyphenated

    def test_should_accept_isbn_13_with_spaces(self) -> None:
        spaced = f"{VALID_ISBN_13[:3]} {VALID_ISBN_13[3:]}"
        isbn_vo = IsbnVO(spaced)

        assert isbn_vo.value == spaced

    def test_should_raise_exception_when_isbn_is_none(self) -> None:
        with pytest.raises(InvalidIsbnException):
            IsbnVO(None)  # type: ignore[arg-type]

    def test_should_raise_exception_when_isbn_is_empty(self) -> None:
        with pytest.raises(InvalidIsbnException):
            IsbnVO("")

    @pytest.mark.parametrize("isbn", [123, True, False, [], {}])
    def test_should_raise_exception_when_isbn_is_not_a_string(self, isbn: Any) -> None:
        with pytest.raises(InvalidIsbnException):
            IsbnVO(isbn)

    @pytest.mark.parametrize(
        "isbn",
        [
            "",
            " ",
            "   ",
            "\t",
            "\n",
            "\r\n",
        ],
    )
    def test_should_raise_exception_when_isbn_is_whitespace_only(
        self, isbn: str
    ) -> None:
        with pytest.raises(InvalidIsbnException):
            IsbnVO(isbn)

    def test_should_raise_exception_when_isbn_10_check_digit_is_invalid(
        self,
    ) -> None:
        invalid = VALID_ISBN_10[:-1] + ("0" if VALID_ISBN_10[-1] != "0" else "1")
        with pytest.raises(InvalidIsbnException):
            IsbnVO(invalid)

    def test_should_raise_exception_when_isbn_13_check_digit_is_invalid(
        self,
    ) -> None:
        invalid = VALID_ISBN_13[:-1] + ("0" if VALID_ISBN_13[-1] != "0" else "1")
        with pytest.raises(InvalidIsbnException):
            IsbnVO(invalid)

    @pytest.mark.parametrize(
        "isbn",
        [
            "123",
            "12345678",
            "123456789012",
            "12345678901234",
        ],
    )
    def test_should_raise_exception_when_isbn_length_is_neither_10_nor_13(
        self, isbn: str
    ) -> None:
        with pytest.raises(InvalidIsbnException):
            IsbnVO(isbn)

    def test_should_raise_exception_when_attempting_to_modify_isbn(self) -> None:
        isbn_vo = IsbnVO(VALID_ISBN_13)

        with pytest.raises(FrozenInstanceError):
            isbn_vo.isbn = VALID_ISBN_10  # type: ignore[misc]
