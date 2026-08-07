from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest

from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.authentication_authorization_exception import (
    InvalidAccessTokenPayloadException,
)
from src.shared.domain.value_objects.access_token_payload_vo import (
    AccessTokenPayloadVO,
)


@pytest.fixture
def valid_jti() -> UUID:
    return uuid4()


@pytest.fixture
def valid_sub() -> UUID:
    return uuid4()


@pytest.fixture
def valid_role() -> UserRoleEnum:
    return UserRoleEnum.MEMBER


@pytest.fixture
def valid_exp() -> datetime:
    return datetime.now(UTC) + timedelta(minutes=10)


class TestAccessTokenPayloadVO:
    def test_should_create_payload_when_data_is_valid(
        self,
        valid_jti: UUID,
        valid_sub: UUID,
        valid_role: UserRoleEnum,
        valid_exp: datetime,
    ) -> None:
        payload_vo = AccessTokenPayloadVO(
            jti=valid_jti,
            sub=valid_sub,
            role=valid_role,
            exp=valid_exp,
        )

        assert payload_vo.jti == valid_jti
        assert payload_vo.sub == valid_sub
        assert payload_vo.role == valid_role
        assert payload_vo.exp == valid_exp

    def test_should_raise_exception_when_jti_is_none(
        self,
        valid_sub: UUID,
        valid_role: UserRoleEnum,
        valid_exp: datetime,
    ) -> None:
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=None,  # type: ignore[arg-type]
                sub=valid_sub,
                role=valid_role,
                exp=valid_exp,
            )

    def test_should_raise_exception_when_sub_is_none(
        self,
        valid_jti: UUID,
        valid_role: UserRoleEnum,
        valid_exp: datetime,
    ) -> None:
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=valid_jti,
                sub=None,  # type: ignore[arg-type]
                role=valid_role,
                exp=valid_exp,
            )

    def test_should_raise_exception_when_role_is_none(
        self,
        valid_jti: UUID,
        valid_sub: UUID,
        valid_exp: datetime,
    ) -> None:
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=valid_jti,
                sub=valid_sub,
                role=None,  # type: ignore[arg-type]
                exp=valid_exp,
            )

    def test_should_raise_exception_when_exp_is_none(
        self,
        valid_jti: UUID,
        valid_sub: UUID,
        valid_role: UserRoleEnum,
    ) -> None:
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=valid_jti,
                sub=valid_sub,
                role=valid_role,
                exp=None,  # type: ignore[arg-type]
            )

    @pytest.mark.parametrize("jti", [123, "not-a-uuid", [], {}])
    def test_should_raise_exception_when_jti_is_not_a_uuid(
        self,
        jti: Any,
        valid_sub: UUID,
        valid_role: UserRoleEnum,
        valid_exp: datetime,
    ) -> None:
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=jti,
                sub=valid_sub,
                role=valid_role,
                exp=valid_exp,
            )

    @pytest.mark.parametrize("sub", [123, "not-a-uuid", [], {}])
    def test_should_raise_exception_when_sub_is_not_a_uuid(
        self,
        sub: Any,
        valid_jti: UUID,
        valid_role: UserRoleEnum,
        valid_exp: datetime,
    ) -> None:
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=valid_jti,
                sub=sub,
                role=valid_role,
                exp=valid_exp,
            )

    @pytest.mark.parametrize("role", [123, "MEMBER", [], {}])
    def test_should_raise_exception_when_role_is_not_a_user_role_enum(
        self,
        role: Any,
        valid_jti: UUID,
        valid_sub: UUID,
        valid_exp: datetime,
    ) -> None:
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=valid_jti,
                sub=valid_sub,
                role=role,
                exp=valid_exp,
            )

    @pytest.mark.parametrize("exp", ["1735689600", 1735689600, 1735689600.5, [], {}])
    def test_should_raise_exception_when_exp_is_not_a_datetime(
        self,
        exp: Any,
        valid_jti: UUID,
        valid_sub: UUID,
        valid_role: UserRoleEnum,
    ) -> None:
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=valid_jti,
                sub=valid_sub,
                role=valid_role,
                exp=exp,
            )

    def test_should_raise_exception_when_exp_is_not_in_the_future(
        self,
        valid_jti: UUID,
        valid_sub: UUID,
        valid_role: UserRoleEnum,
    ) -> None:
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=valid_jti,
                sub=valid_sub,
                role=valid_role,
                exp=datetime.now(UTC) - timedelta(seconds=1),
            )

    def test_should_raise_exception_when_exp_is_timezone_naive(
        self,
        valid_jti: UUID,
        valid_sub: UUID,
        valid_role: UserRoleEnum,
    ) -> None:
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=valid_jti,
                sub=valid_sub,
                role=valid_role,
                exp=datetime.now(),
            )

    def test_should_be_immutable_when_created(
        self,
        valid_jti: UUID,
        valid_sub: UUID,
        valid_role: UserRoleEnum,
        valid_exp: datetime,
    ) -> None:
        payload_vo = AccessTokenPayloadVO(
            jti=valid_jti,
            sub=valid_sub,
            role=valid_role,
            exp=valid_exp,
        )

        with pytest.raises(FrozenInstanceError):
            payload_vo.exp = valid_exp + timedelta(minutes=1)  # type: ignore[misc]

    def test_should_return_payload_as_dict_when_to_dict_is_called(
        self,
        valid_jti: UUID,
        valid_sub: UUID,
        valid_role: UserRoleEnum,
        valid_exp: datetime,
    ) -> None:
        payload_vo = AccessTokenPayloadVO(
            jti=valid_jti,
            sub=valid_sub,
            role=valid_role,
            exp=valid_exp,
        )

        assert payload_vo.to_dict() == {
            "jti": str(valid_jti),
            "sub": str(valid_sub),
            "role": valid_role.value,
            "exp": int(valid_exp.timestamp()),
        }
