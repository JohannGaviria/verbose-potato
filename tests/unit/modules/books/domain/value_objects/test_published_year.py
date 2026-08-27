from dataclasses import FrozenInstanceError
from datetime import date
from typing import Any

import pytest

from src.modules.books.domain.exceptions.book_exception import (
    InvalidPublishedYearException,
)
from src.modules.books.domain.value_objects.published_year_vo import PublishedYearVO


class TestPublishedYearVO:
    def test_should_return_published_year_as_int_when_valid_year_is_provided(
        self,
    ) -> None:
        published_year_vo = PublishedYearVO(2020)

        assert published_year_vo.value == 2020

    def test_should_raise_exception_when_published_year_is_none(self) -> None:
        with pytest.raises(InvalidPublishedYearException):
            PublishedYearVO(None)  # type: ignore[arg-type]

    @pytest.mark.parametrize("published_year", [True, False])
    def test_should_raise_exception_when_published_year_is_a_boolean(
        self, published_year: bool
    ) -> None:
        with pytest.raises(InvalidPublishedYearException):
            PublishedYearVO(published_year)  # type: ignore[arg-type]

    @pytest.mark.parametrize("published_year", ["2020", 2020.5, [], {}])
    def test_should_raise_exception_when_published_year_is_not_an_integer(
        self, published_year: Any
    ) -> None:
        with pytest.raises(InvalidPublishedYearException):
            PublishedYearVO(published_year)

    def test_should_raise_exception_when_published_year_is_earlier_than_1450(
        self,
    ) -> None:
        with pytest.raises(InvalidPublishedYearException):
            PublishedYearVO(1449)

    def test_should_not_raise_exception_when_published_year_is_exactly_1450(
        self,
    ) -> None:
        published_year_vo = PublishedYearVO(1450)

        assert published_year_vo.value == 1450

    def test_should_raise_exception_when_published_year_is_in_the_future(
        self,
    ) -> None:
        with pytest.raises(InvalidPublishedYearException):
            PublishedYearVO(date.today().year + 1)

    def test_should_not_raise_exception_when_published_year_is_the_current_year(
        self,
    ) -> None:
        current_year = date.today().year
        published_year_vo = PublishedYearVO(current_year)

        assert published_year_vo.value == current_year

    def test_should_raise_exception_when_attempting_to_modify_published_year(
        self,
    ) -> None:
        published_year_vo = PublishedYearVO(2020)

        with pytest.raises(FrozenInstanceError):
            published_year_vo.published_year = 2021  # type: ignore[misc]
