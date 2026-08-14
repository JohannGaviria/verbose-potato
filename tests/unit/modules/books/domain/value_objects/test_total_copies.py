from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from src.modules.books.domain.exceptions.book_exception import (
    InvalidTotalCopiesException,
)
from src.modules.books.domain.value_objects.total_copies_vo import TotalCopiesVO


class TestTotalCopiesVO:
    def test_should_return_total_copies_as_int_when_valid_value_is_provided(
        self,
    ) -> None:
        total_copies_vo = TotalCopiesVO(5)

        assert total_copies_vo.value == 5

    def test_should_raise_exception_when_total_copies_is_none(self) -> None:
        with pytest.raises(InvalidTotalCopiesException):
            TotalCopiesVO(None)  # type: ignore[arg-type]

    @pytest.mark.parametrize("total_copies", [True, False])
    def test_should_raise_exception_when_total_copies_is_a_boolean(
        self, total_copies: bool
    ) -> None:
        with pytest.raises(InvalidTotalCopiesException):
            TotalCopiesVO(total_copies)  # type: ignore[arg-type]

    @pytest.mark.parametrize("total_copies", ["5", 5.5, [], {}])
    def test_should_raise_exception_when_total_copies_is_not_an_integer(
        self, total_copies: Any
    ) -> None:
        with pytest.raises(InvalidTotalCopiesException):
            TotalCopiesVO(total_copies)

    def test_should_raise_exception_when_total_copies_is_zero(self) -> None:
        with pytest.raises(InvalidTotalCopiesException):
            TotalCopiesVO(0)

    def test_should_raise_exception_when_total_copies_is_negative(self) -> None:
        with pytest.raises(InvalidTotalCopiesException):
            TotalCopiesVO(-1)

    def test_should_not_raise_exception_when_total_copies_is_exactly_one(
        self,
    ) -> None:
        total_copies_vo = TotalCopiesVO(1)

        assert total_copies_vo.value == 1

    def test_should_raise_exception_when_attempting_to_modify_total_copies(
        self,
    ) -> None:
        total_copies_vo = TotalCopiesVO(5)

        with pytest.raises(FrozenInstanceError):
            total_copies_vo.total_copies = 10  # type: ignore[misc]
