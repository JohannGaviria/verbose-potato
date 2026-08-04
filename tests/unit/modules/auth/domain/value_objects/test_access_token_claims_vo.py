from dataclasses import FrozenInstanceError
from typing import Any
from uuid import UUID, uuid4

import pytest

from src.modules.auth.domain.exceptions.authentication_exception import (
    InvalidAccessTokenClaimsException,
)
from src.modules.auth.domain.value_objects.access_token_claims_vo import (
    AccessTokenClaimsVO,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum


@pytest.fixture
def valid_jti() -> UUID:
    return uuid4()


@pytest.fixture
def valid_sub() -> UUID:
    return uuid4()


@pytest.fixture
def valid_role() -> UserRoleEnum:
    return UserRoleEnum.MEMBER


class TestAccessTokenClaimsVO:
    def test_should_create_claims_when_data_is_valid(
        self, valid_jti: UUID, valid_sub: UUID, valid_role: UserRoleEnum
    ) -> None:
        claims_vo = AccessTokenClaimsVO(jti=valid_jti, sub=valid_sub, role=valid_role)

        assert claims_vo.jti == valid_jti
        assert claims_vo.sub == valid_sub
        assert claims_vo.role == valid_role

    def test_should_raise_exception_when_jti_is_none(
        self, valid_sub: UUID, valid_role: UserRoleEnum
    ) -> None:
        with pytest.raises(InvalidAccessTokenClaimsException):
            AccessTokenClaimsVO(jti=None, sub=valid_sub, role=valid_role)  # type: ignore[arg-type]

    def test_should_raise_exception_when_sub_is_none(
        self, valid_jti: UUID, valid_role: UserRoleEnum
    ) -> None:
        with pytest.raises(InvalidAccessTokenClaimsException):
            AccessTokenClaimsVO(jti=valid_jti, sub=None, role=valid_role)  # type: ignore[arg-type]

    def test_should_raise_exception_when_role_is_none(
        self, valid_jti: UUID, valid_sub: UUID
    ) -> None:
        with pytest.raises(InvalidAccessTokenClaimsException):
            AccessTokenClaimsVO(jti=valid_jti, sub=valid_sub, role=None)  # type: ignore[arg-type]

    @pytest.mark.parametrize("jti", [123, "not-a-uuid", [], {}])
    def test_should_raise_exception_when_jti_is_not_a_uuid(
        self, jti: Any, valid_sub: UUID, valid_role: UserRoleEnum
    ) -> None:
        with pytest.raises(InvalidAccessTokenClaimsException):
            AccessTokenClaimsVO(jti=jti, sub=valid_sub, role=valid_role)

    @pytest.mark.parametrize("sub", [123, "not-a-uuid", [], {}])
    def test_should_raise_exception_when_sub_is_not_a_uuid(
        self, sub: Any, valid_jti: UUID, valid_role: UserRoleEnum
    ) -> None:
        with pytest.raises(InvalidAccessTokenClaimsException):
            AccessTokenClaimsVO(jti=valid_jti, sub=sub, role=valid_role)

    @pytest.mark.parametrize("role", [123, "MEMBER", [], {}])
    def test_should_raise_exception_when_role_is_not_a_user_role_enum(
        self, role: Any, valid_jti: UUID, valid_sub: UUID
    ) -> None:
        with pytest.raises(InvalidAccessTokenClaimsException):
            AccessTokenClaimsVO(jti=valid_jti, sub=valid_sub, role=role)

    def test_should_be_immutable_when_created(
        self, valid_jti: UUID, valid_sub: UUID, valid_role: UserRoleEnum
    ) -> None:
        claims_vo = AccessTokenClaimsVO(jti=valid_jti, sub=valid_sub, role=valid_role)

        with pytest.raises(FrozenInstanceError):
            claims_vo.jti = uuid4()  # type: ignore[misc]

    def test_should_create_instance_with_generated_jti_when_using_create_factory_method(
        self, valid_sub: UUID, valid_role: UserRoleEnum
    ) -> None:
        claims_vo = AccessTokenClaimsVO.create(sub=valid_sub, role=valid_role)

        assert isinstance(claims_vo.jti, UUID)
        assert claims_vo.sub == valid_sub
        assert claims_vo.role == valid_role

    def test_should_generate_unique_jti_for_each_create_call(
        self, valid_sub: UUID, valid_role: UserRoleEnum
    ) -> None:
        first_claims_vo = AccessTokenClaimsVO.create(sub=valid_sub, role=valid_role)
        second_claims_vo = AccessTokenClaimsVO.create(sub=valid_sub, role=valid_role)

        assert first_claims_vo.jti != second_claims_vo.jti
