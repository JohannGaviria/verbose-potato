from dataclasses import FrozenInstanceError
from typing import Any
from uuid import uuid4

import pytest

from src.modules.loans.domain.enums.loan_sort_by_enum import LoanSortByEnum
from src.modules.loans.domain.enums.loan_status_enum import LoanStatusEnum
from src.modules.loans.domain.exceptions.loan_exception import (
    InvalidLoanCatalogQueryException,
)
from src.modules.loans.domain.value_objects.loan_catalog_query_vo import (
    LoanCatalogQueryVO,
)
from src.shared.domain.enums.sort_order_enum import SortOrderEnum

_DEFAULTS: dict[str, Any] = {
    "member_id": None,
    "book_id": None,
    "status": None,
    "sort_by": None,
    "sort_order": None,
    "page": 1,
    "page_size": 20,
}


def _build_query(**overrides: Any) -> LoanCatalogQueryVO:
    data = {**_DEFAULTS, **overrides}
    return LoanCatalogQueryVO(**data)


class TestLoanCatalogQueryVO:
    def test_should_create_query_when_all_filters_are_none(self) -> None:
        query = _build_query()

        assert query.member_id is None
        assert query.book_id is None
        assert query.status is None
        assert query.sort_by is None
        assert query.sort_order is None
        assert query.page == 1
        assert query.page_size == 20

    def test_should_create_query_when_all_filters_are_provided(self) -> None:
        member_id = uuid4()
        book_id = uuid4()
        query = _build_query(
            member_id=member_id,
            book_id=book_id,
            status=LoanStatusEnum.RETURNED,
            sort_by=LoanSortByEnum.RETURNED_AT,
            sort_order=SortOrderEnum.DESC,
            page=3,
            page_size=50,
        )

        assert query.member_id == member_id
        assert query.book_id == book_id
        assert query.status == LoanStatusEnum.RETURNED
        assert query.sort_by == LoanSortByEnum.RETURNED_AT
        assert query.sort_order == SortOrderEnum.DESC
        assert query.page == 3
        assert query.page_size == 50

    def test_should_not_raise_exception_when_member_id_is_a_valid_uuid(self) -> None:
        member_id = uuid4()
        query = _build_query(member_id=member_id)

        assert query.member_id == member_id

    @pytest.mark.parametrize("member_id", ["abc", 1, True, str(uuid4())])
    def test_should_raise_exception_when_member_id_is_invalid(
        self, member_id: Any
    ) -> None:
        with pytest.raises(InvalidLoanCatalogQueryException):
            _build_query(member_id=member_id)

    def test_should_not_raise_exception_when_book_id_is_a_valid_uuid(self) -> None:
        book_id = uuid4()
        query = _build_query(book_id=book_id)

        assert query.book_id == book_id

    @pytest.mark.parametrize("book_id", ["abc", 1, True, str(uuid4())])
    def test_should_raise_exception_when_book_id_is_invalid(self, book_id: Any) -> None:
        with pytest.raises(InvalidLoanCatalogQueryException):
            _build_query(book_id=book_id)

    @pytest.mark.parametrize(
        "status", [LoanStatusEnum.ACTIVE, LoanStatusEnum.RETURNED, None]
    )
    def test_should_not_raise_exception_when_status_is_valid(
        self, status: LoanStatusEnum | None
    ) -> None:
        query = _build_query(status=status)

        assert query.status == status

    @pytest.mark.parametrize("status", ["ACTIVE", "RETURNED", "PENDING", 1])
    def test_should_raise_exception_when_status_is_not_a_valid_enum_member(
        self, status: Any
    ) -> None:
        with pytest.raises(InvalidLoanCatalogQueryException):
            _build_query(status=status)

    @pytest.mark.parametrize(
        "sort_by", [LoanSortByEnum.LOANED_AT, LoanSortByEnum.RETURNED_AT, None]
    )
    def test_should_not_raise_exception_when_sort_by_is_valid(
        self, sort_by: LoanSortByEnum | None
    ) -> None:
        query = _build_query(sort_by=sort_by)

        assert query.sort_by == sort_by

    @pytest.mark.parametrize("sort_by", ["loaned_at", "returned_at", 1])
    def test_should_raise_exception_when_sort_by_is_not_a_valid_enum_member(
        self, sort_by: Any
    ) -> None:
        with pytest.raises(InvalidLoanCatalogQueryException):
            _build_query(sort_by=sort_by)

    @pytest.mark.parametrize(
        "sort_order", [SortOrderEnum.ASC, SortOrderEnum.DESC, None]
    )
    def test_should_not_raise_exception_when_sort_order_is_valid(
        self, sort_order: SortOrderEnum | None
    ) -> None:
        query = _build_query(sort_order=sort_order)

        assert query.sort_order == sort_order

    @pytest.mark.parametrize("sort_order", ["asc", "desc", 1])
    def test_should_raise_exception_when_sort_order_is_not_a_valid_enum_member(
        self, sort_order: Any
    ) -> None:
        with pytest.raises(InvalidLoanCatalogQueryException):
            _build_query(sort_order=sort_order)

    @pytest.mark.parametrize("page", [1, 2, 100])
    def test_should_not_raise_exception_when_page_is_valid(self, page: int) -> None:
        query = _build_query(page=page)

        assert query.page == page

    @pytest.mark.parametrize("page", [0, -1, True, False, "1", None, 1.5])
    def test_should_raise_exception_when_page_is_invalid(self, page: Any) -> None:
        with pytest.raises(InvalidLoanCatalogQueryException):
            _build_query(page=page)

    @pytest.mark.parametrize("page_size", [1, 20, 100])
    def test_should_not_raise_exception_when_page_size_is_valid(
        self, page_size: int
    ) -> None:
        query = _build_query(page_size=page_size)

        assert query.page_size == page_size

    @pytest.mark.parametrize(
        "page_size", [0, -1, True, False, "20", None, 1.5, 101, 1000]
    )
    def test_should_raise_exception_when_page_size_is_invalid(
        self, page_size: Any
    ) -> None:
        with pytest.raises(InvalidLoanCatalogQueryException):
            _build_query(page_size=page_size)

    def test_should_raise_exception_when_attempting_to_modify_query(self) -> None:
        query = _build_query()

        with pytest.raises(FrozenInstanceError):
            query.page = 2  # type: ignore[misc]

    def test_should_be_equal_when_queries_have_same_values(self) -> None:
        first = _build_query(page=2, page_size=10)
        second = _build_query(page=2, page_size=10)

        assert first == second

    def test_should_not_be_equal_when_queries_have_different_values(self) -> None:
        first = _build_query(page=1)
        second = _build_query(page=2)

        assert first != second
