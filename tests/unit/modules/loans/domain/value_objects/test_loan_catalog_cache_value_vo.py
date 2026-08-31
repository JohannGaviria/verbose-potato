from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from src.modules.loans.domain.value_objects.loan_catalog_cache_value_vo import (
    LoanCatalogCacheValueVO,
)
from src.shared.domain.exceptions.cache_exception import InvalidCacheEntryException

_VALID_ITEM = {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "member_id": "2fa85f64-5717-4562-b3fc-2c963f66afa6",
    "book_id": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
    "status": "ACTIVE",
    "loaned_at": "2024-01-01T00:00:00+00:00",
    "returned_at": None,
}

_DEFAULTS: dict[str, Any] = {
    "items": (_VALID_ITEM,),
    "total": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
}


def _build_value(**overrides: Any) -> LoanCatalogCacheValueVO:
    data = {**_DEFAULTS, **overrides}
    return LoanCatalogCacheValueVO(**data)


class TestLoanCatalogCacheValueVO:
    def test_should_create_value_when_data_is_valid(self) -> None:
        value = _build_value()

        assert value.items == (_VALID_ITEM,)
        assert value.total == 1
        assert value.page == 1
        assert value.page_size == 20
        assert value.total_pages == 1

    def test_should_create_value_when_items_is_empty(self) -> None:
        value = _build_value(items=(), total=0, total_pages=0)

        assert value.items == ()
        assert value.total == 0
        assert value.total_pages == 0

    @pytest.mark.parametrize("items", [[_VALID_ITEM], "items", None, _VALID_ITEM])
    def test_should_raise_exception_when_items_is_not_a_tuple(self, items: Any) -> None:
        with pytest.raises(InvalidCacheEntryException):
            _build_value(items=items)

    @pytest.mark.parametrize("total", ["1", None, 1.5, True, False])
    def test_should_raise_exception_when_total_is_not_an_integer(
        self, total: Any
    ) -> None:
        with pytest.raises(InvalidCacheEntryException):
            _build_value(total=total)

    def test_should_raise_exception_when_total_is_negative(self) -> None:
        with pytest.raises(InvalidCacheEntryException):
            _build_value(total=-1)

    def test_should_not_raise_exception_when_total_is_zero(self) -> None:
        value = _build_value(total=0, items=(), total_pages=0)

        assert value.total == 0

    @pytest.mark.parametrize("page", ["1", None, 1.5, True, False])
    def test_should_raise_exception_when_page_is_not_an_integer(
        self, page: Any
    ) -> None:
        with pytest.raises(InvalidCacheEntryException):
            _build_value(page=page)

    def test_should_raise_exception_when_page_is_less_than_one(self) -> None:
        with pytest.raises(InvalidCacheEntryException):
            _build_value(page=0)

    @pytest.mark.parametrize("page_size", ["20", None, 1.5, True, False])
    def test_should_raise_exception_when_page_size_is_not_an_integer(
        self, page_size: Any
    ) -> None:
        with pytest.raises(InvalidCacheEntryException):
            _build_value(page_size=page_size)

    def test_should_raise_exception_when_page_size_is_less_than_one(self) -> None:
        with pytest.raises(InvalidCacheEntryException):
            _build_value(page_size=0)

    @pytest.mark.parametrize("total_pages", ["1", None, 1.5, True, False])
    def test_should_raise_exception_when_total_pages_is_not_an_integer(
        self, total_pages: Any
    ) -> None:
        with pytest.raises(InvalidCacheEntryException):
            _build_value(total_pages=total_pages)

    def test_should_raise_exception_when_total_pages_is_negative(self) -> None:
        with pytest.raises(InvalidCacheEntryException):
            _build_value(total_pages=-1)

    def test_should_not_raise_exception_when_total_pages_is_zero(self) -> None:
        value = _build_value(total_pages=0)

        assert value.total_pages == 0

    def test_should_return_dict_when_to_dict_is_called(self) -> None:
        value = _build_value()

        assert value.to_dict() == {
            "items": [_VALID_ITEM],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "total_pages": 1,
        }

    def test_should_rebuild_value_when_from_dict_is_called(self) -> None:
        value = _build_value()

        rebuilt = LoanCatalogCacheValueVO.from_dict(value.to_dict())

        assert rebuilt == value

    def test_should_be_immutable_when_created(self) -> None:
        value = _build_value()

        with pytest.raises(FrozenInstanceError):
            value.total = 2  # type: ignore[misc]

    def test_should_be_equal_when_values_have_same_data(self) -> None:
        first = _build_value()
        second = _build_value()

        assert first == second

    def test_should_not_be_equal_when_values_have_different_data(self) -> None:
        first = _build_value(total=1)
        second = _build_value(total=2)

        assert first != second
