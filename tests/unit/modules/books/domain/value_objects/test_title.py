from dataclasses import FrozenInstanceError
from typing import Any

import pytest
from faker import Faker

from src.modules.books.domain.exceptions.book_exception import InvalidTitleException
from src.modules.books.domain.value_objects.title_vo import TitleVO


class TestTitleVO:
    def test_should_return_title_as_string_when_valid_title_is_provided(
        self, faker: Faker
    ) -> None:
        title = faker.sentence(nb_words=4)
        title_vo = TitleVO(title)

        assert title_vo.value == title

    def test_should_raise_exception_when_title_is_none(self) -> None:
        with pytest.raises(InvalidTitleException):
            TitleVO(None)  # type: ignore[arg-type]

    def test_should_raise_exception_when_title_is_empty(self) -> None:
        with pytest.raises(InvalidTitleException):
            TitleVO("")

    @pytest.mark.parametrize("title", [123, True, False, [], {}])
    def test_should_raise_exception_when_title_is_not_a_string(
        self, title: Any
    ) -> None:
        with pytest.raises(InvalidTitleException):
            TitleVO(title)

    @pytest.mark.parametrize(
        "title",
        [
            "",
            " ",
            "   ",
            "\t",
            "\n",
            "\r\n",
        ],
    )
    def test_should_raise_exception_when_title_is_whitespace_only(
        self, title: str
    ) -> None:
        with pytest.raises(InvalidTitleException):
            TitleVO(title)

    @pytest.mark.parametrize(
        "title",
        [
            "a",
            "ab",
        ],
    )
    def test_should_raise_exception_when_title_is_too_short(self, title: str) -> None:
        with pytest.raises(InvalidTitleException):
            TitleVO(title)

    def test_should_raise_exception_when_title_exceeds_max_length(self) -> None:
        with pytest.raises(InvalidTitleException):
            TitleVO("a" * 256)

    def test_should_not_raise_exception_when_title_is_at_min_length(self) -> None:
        title_vo = TitleVO("abc")

        assert title_vo.value == "abc"

    def test_should_not_raise_exception_when_title_is_at_max_length(self) -> None:
        title = "a" * 255
        title_vo = TitleVO(title)

        assert title_vo.value == title

    def test_should_raise_exception_when_attempting_to_modify_title(
        self, faker: Faker
    ) -> None:
        title_vo = TitleVO(faker.sentence(nb_words=4))

        with pytest.raises(FrozenInstanceError):
            title_vo.title = faker.sentence(nb_words=4)  # type: ignore[misc]
