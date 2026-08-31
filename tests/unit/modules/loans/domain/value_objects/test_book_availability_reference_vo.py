from dataclasses import FrozenInstanceError

import pytest
from faker import Faker

from src.modules.loans.domain.exceptions.book_reference_exception import (
    BookNotAvailableException,
)
from src.modules.loans.domain.value_objects.book_availability_reference_vo import (
    BookAvailabilityReferenceVO,
)


def _build_vo(faker: Faker, available_copies: int = 3) -> BookAvailabilityReferenceVO:
    return BookAvailabilityReferenceVO(
        book_id=faker.uuid4(cast_to=None),
        available_copies=available_copies,
    )


class TestBookAvailabilityReferenceVO:
    def test_should_create_vo_when_valid_data_is_provided(self, faker: Faker) -> None:
        book_id = faker.uuid4(cast_to=None)
        available_copies = 5

        vo = BookAvailabilityReferenceVO(
            book_id=book_id, available_copies=available_copies
        )

        assert vo.book_id == book_id
        assert vo.available_copies == available_copies

    def test_should_raise_exception_when_attempting_to_modify_available_copies(
        self, faker: Faker
    ) -> None:
        vo = _build_vo(faker)

        with pytest.raises(FrozenInstanceError):
            vo.available_copies = 10  # type: ignore[misc]

    def test_should_return_equal_vos_when_data_is_identical(self, faker: Faker) -> None:
        book_id = faker.uuid4(cast_to=None)

        vo1 = BookAvailabilityReferenceVO(book_id=book_id, available_copies=3)
        vo2 = BookAvailabilityReferenceVO(book_id=book_id, available_copies=3)

        assert vo1 == vo2

    def test_should_return_different_vos_when_available_copies_differ(
        self, faker: Faker
    ) -> None:
        book_id = faker.uuid4(cast_to=None)

        vo1 = BookAvailabilityReferenceVO(book_id=book_id, available_copies=3)
        vo2 = BookAvailabilityReferenceVO(book_id=book_id, available_copies=2)

        assert vo1 != vo2

    @pytest.mark.parametrize("available_copies", [1, 2, 5])
    def test_should_not_raise_when_book_has_available_copies(
        self, faker: Faker, available_copies: int
    ) -> None:
        vo = _build_vo(faker, available_copies=available_copies)

        vo.ensure_has_available_copies()

    @pytest.mark.parametrize("available_copies", [0, -1])
    def test_should_raise_book_not_available_exception_when_no_copies_are_available(
        self, faker: Faker, available_copies: int
    ) -> None:
        vo = _build_vo(faker, available_copies=available_copies)

        with pytest.raises(BookNotAvailableException):
            vo.ensure_has_available_copies()

    def test_should_reduce_available_copies_by_one_when_copies_are_available(
        self, faker: Faker
    ) -> None:
        vo = _build_vo(faker, available_copies=3)

        result = vo.reduce_available_copies()

        assert result == 2

    def test_should_not_mutate_the_vo_when_reducing_available_copies(
        self, faker: Faker
    ) -> None:
        vo = _build_vo(faker, available_copies=3)

        vo.reduce_available_copies()

        assert vo.available_copies == 3

    def test_should_raise_book_not_available_exception_when_reducing_with_no_available_copies(
        self, faker: Faker
    ) -> None:
        vo = _build_vo(faker, available_copies=0)

        with pytest.raises(BookNotAvailableException):
            vo.reduce_available_copies()

    def test_should_increase_available_copies_by_one(self, faker: Faker) -> None:
        vo = _build_vo(faker, available_copies=3)

        result = vo.increase_available_copies()

        assert result == 4

    def test_should_increase_available_copies_by_one_even_when_starting_from_zero(
        self, faker: Faker
    ) -> None:
        vo = _build_vo(faker, available_copies=0)

        result = vo.increase_available_copies()

        assert result == 1

    def test_should_not_mutate_the_vo_when_increasing_available_copies(
        self, faker: Faker
    ) -> None:
        vo = _build_vo(faker, available_copies=3)

        vo.increase_available_copies()

        assert vo.available_copies == 3
