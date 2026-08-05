from dataclasses import FrozenInstanceError
from typing import Any

import pytest
from faker import Faker

from src.modules.auth.domain.exceptions.authentication_exception import (
    InvalidAccessTokenResultException,
)
from src.modules.auth.domain.value_objects.access_token_result_vo import (
    AccessTokenResultVO,
)
from src.modules.auth.domain.value_objects.access_token_vo import AccessTokenVO


@pytest.fixture
def valid_access_token(faker: Faker) -> AccessTokenVO:
    return AccessTokenVO(faker.sha256())


@pytest.fixture
def valid_token_type() -> str:
    return "Bearer"


@pytest.fixture
def valid_expires_in() -> int:
    return 3600


class TestAccessTokenResultVO:
    def test_should_create_access_token_result_when_data_is_valid(
        self,
        valid_access_token: AccessTokenVO,
        valid_token_type: str,
        valid_expires_in: int,
    ) -> None:
        result_vo = AccessTokenResultVO(
            access_token=valid_access_token,
            token_type=valid_token_type,
            expires_in=valid_expires_in,
        )

        assert result_vo.access_token == valid_access_token
        assert result_vo.token_type == valid_token_type
        assert result_vo.expires_in == valid_expires_in

    def test_should_raise_exception_when_access_token_is_none(
        self, valid_token_type: str, valid_expires_in: int
    ) -> None:
        with pytest.raises(InvalidAccessTokenResultException):
            AccessTokenResultVO(
                access_token=None,  # type: ignore[arg-type]
                token_type=valid_token_type,
                expires_in=valid_expires_in,
            )

    def test_should_raise_exception_when_token_type_is_none(
        self, valid_access_token: AccessTokenVO, valid_expires_in: int
    ) -> None:
        with pytest.raises(InvalidAccessTokenResultException):
            AccessTokenResultVO(
                access_token=valid_access_token,
                token_type=None,  # type: ignore[arg-type]
                expires_in=valid_expires_in,
            )

    def test_should_raise_exception_when_expires_in_is_none(
        self, valid_access_token: AccessTokenVO, valid_token_type: str
    ) -> None:
        with pytest.raises(InvalidAccessTokenResultException):
            AccessTokenResultVO(
                access_token=valid_access_token,
                token_type=valid_token_type,
                expires_in=None,  # type: ignore[arg-type]
            )

    def test_should_raise_exception_when_access_token_is_not_an_access_token_vo(
        self, valid_token_type: str, valid_expires_in: int
    ) -> None:
        with pytest.raises(InvalidAccessTokenResultException):
            AccessTokenResultVO(
                access_token="not-a-token",  # type: ignore[arg-type]
                token_type=valid_token_type,
                expires_in=valid_expires_in,
            )

    @pytest.mark.parametrize("token_type", [123, True, False, [], {}])
    def test_should_raise_exception_when_token_type_is_not_a_string(
        self,
        token_type: Any,
        valid_access_token: AccessTokenVO,
        valid_expires_in: int,
    ) -> None:
        with pytest.raises(InvalidAccessTokenResultException):
            AccessTokenResultVO(
                access_token=valid_access_token,
                token_type=token_type,
                expires_in=valid_expires_in,
            )

    @pytest.mark.parametrize("expires_in", ["3600", 3600.5, [], {}])
    def test_should_raise_exception_when_expires_in_is_not_an_integer(
        self,
        expires_in: Any,
        valid_access_token: AccessTokenVO,
        valid_token_type: str,
    ) -> None:
        with pytest.raises(InvalidAccessTokenResultException):
            AccessTokenResultVO(
                access_token=valid_access_token,
                token_type=valid_token_type,
                expires_in=expires_in,
            )

    def test_should_raise_exception_when_expires_in_is_zero(
        self, valid_access_token: AccessTokenVO, valid_token_type: str
    ) -> None:
        with pytest.raises(InvalidAccessTokenResultException):
            AccessTokenResultVO(
                access_token=valid_access_token,
                token_type=valid_token_type,
                expires_in=0,
            )

    def test_should_raise_exception_when_expires_in_is_negative(
        self, valid_access_token: AccessTokenVO, valid_token_type: str
    ) -> None:
        with pytest.raises(InvalidAccessTokenResultException):
            AccessTokenResultVO(
                access_token=valid_access_token,
                token_type=valid_token_type,
                expires_in=-1,
            )

    def test_should_be_immutable_when_created(
        self,
        valid_access_token: AccessTokenVO,
        valid_token_type: str,
        valid_expires_in: int,
    ) -> None:
        result_vo = AccessTokenResultVO(
            access_token=valid_access_token,
            token_type=valid_token_type,
            expires_in=valid_expires_in,
        )

        with pytest.raises(FrozenInstanceError):
            result_vo.expires_in = 7200  # type: ignore[misc]
