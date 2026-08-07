from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from src.config import settings
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.authentication_authorization_exception import (
    ExpiredAccessTokenException,
    InvalidAccessTokenException,
)
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.domain.value_objects.access_token_vo import AccessTokenVO
from src.shared.infrastructure.outbound.pyjwt_toke_decode_outbound_adapter import (
    PyJWTTokenDecodeOutboundAdapter,
)

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM


def encode_raw_token(
    payload: dict, secret: str = JWT_SECRET_KEY, algorithm: str = JWT_ALGORITHM
) -> str:
    """Encode a payload with the real PyJWT library, bypassing the token_decode_outbound.

    Used to build tokens (including malformed/incomplete ones) the same way
    an external issuer would, so the token_decode_outbound is exercised against a real
    JWT rather than a hand-crafted string.
    """
    return jwt.encode(payload, secret, algorithm=algorithm)


def make_claims(
    *,
    jti: str | None = None,
    sub: str | None = None,
    role: str = UserRoleEnum.MEMBER.value,
    expires_in_seconds: int = 60,
) -> dict:
    """A well-formed set of JWT claims matching what the token generator adapter emits."""
    return {
        "jti": jti if jti is not None else str(uuid4()),
        "sub": sub if sub is not None else str(uuid4()),
        "role": role,
        "exp": int(
            (datetime.now(UTC) + timedelta(seconds=expires_in_seconds)).timestamp()
        ),
    }


class TestPyJWTTokenDecodeOutboundAdapter:
    class TestDecode:
        def test_should_return_access_token_payload_when_token_is_valid(
            self, token_decode_outbound: PyJWTTokenDecodeOutboundAdapter
        ) -> None:
            claims = make_claims(role=UserRoleEnum.LIBRARIAN.value)
            token = AccessTokenVO(encode_raw_token(claims))

            result = token_decode_outbound.decode(token)

            assert isinstance(result, AccessTokenPayloadVO)
            assert str(result.jti) == claims["jti"]
            assert str(result.sub) == claims["sub"]
            assert result.role == UserRoleEnum.LIBRARIAN
            assert int(result.exp.timestamp()) == claims["exp"]

        def test_should_return_a_timezone_aware_expiration(
            self, token_decode_outbound: PyJWTTokenDecodeOutboundAdapter
        ) -> None:
            token = AccessTokenVO(encode_raw_token(make_claims()))

            result = token_decode_outbound.decode(token)

            assert result.exp.tzinfo is not None

        def test_should_raise_expired_access_token_exception_when_token_has_expired(
            self, token_decode_outbound: PyJWTTokenDecodeOutboundAdapter
        ) -> None:
            claims = make_claims(expires_in_seconds=-60)
            token = AccessTokenVO(encode_raw_token(claims))

            with pytest.raises(ExpiredAccessTokenException):
                token_decode_outbound.decode(token)

        def test_should_raise_invalid_access_token_exception_when_signature_does_not_match(
            self, token_decode_outbound: PyJWTTokenDecodeOutboundAdapter
        ) -> None:
            token = AccessTokenVO(
                encode_raw_token(
                    make_claims(), secret="a-completely-different-secret-key"
                )
            )

            with pytest.raises(InvalidAccessTokenException):
                token_decode_outbound.decode(token)

        def test_should_raise_invalid_access_token_exception_when_algorithm_does_not_match(
            self, token_decode_outbound: PyJWTTokenDecodeOutboundAdapter
        ) -> None:
            token = AccessTokenVO(encode_raw_token(make_claims(), algorithm="HS512"))

            with pytest.raises(InvalidAccessTokenException):
                token_decode_outbound.decode(token)

        def test_should_raise_invalid_access_token_exception_when_token_is_malformed(
            self, token_decode_outbound: PyJWTTokenDecodeOutboundAdapter
        ) -> None:
            token = AccessTokenVO("this-is-not-a-valid-jwt-token")

            with pytest.raises(InvalidAccessTokenException):
                token_decode_outbound.decode(token)

        def test_should_raise_invalid_access_token_exception_when_token_is_not_yet_a_jwt_at_all(
            self, token_decode_outbound: PyJWTTokenDecodeOutboundAdapter
        ) -> None:
            token = AccessTokenVO("a.b")

            with pytest.raises(InvalidAccessTokenException):
                token_decode_outbound.decode(token)

        @pytest.mark.parametrize("missing_claim", ["jti", "sub", "role", "exp"])
        def test_should_raise_invalid_access_token_exception_when_a_required_claim_is_missing(
            self,
            token_decode_outbound: PyJWTTokenDecodeOutboundAdapter,
            missing_claim: str,
        ) -> None:
            claims = make_claims()
            del claims[missing_claim]
            token = AccessTokenVO(encode_raw_token(claims))

            with pytest.raises(InvalidAccessTokenException):
                token_decode_outbound.decode(token)

        def test_should_raise_invalid_access_token_exception_when_jti_is_not_a_valid_uuid(
            self, token_decode_outbound: PyJWTTokenDecodeOutboundAdapter
        ) -> None:
            claims = make_claims(jti="not-a-uuid")
            token = AccessTokenVO(encode_raw_token(claims))

            with pytest.raises(InvalidAccessTokenException):
                token_decode_outbound.decode(token)

        def test_should_raise_invalid_access_token_exception_when_sub_is_not_a_valid_uuid(
            self, token_decode_outbound: PyJWTTokenDecodeOutboundAdapter
        ) -> None:
            claims = make_claims(sub="not-a-uuid")
            token = AccessTokenVO(encode_raw_token(claims))

            with pytest.raises(InvalidAccessTokenException):
                token_decode_outbound.decode(token)

        def test_should_raise_invalid_access_token_exception_when_role_is_not_a_known_role(
            self, token_decode_outbound: PyJWTTokenDecodeOutboundAdapter
        ) -> None:
            claims = make_claims(role="NOT_A_REAL_ROLE")
            token = AccessTokenVO(encode_raw_token(claims))

            with pytest.raises(InvalidAccessTokenException):
                token_decode_outbound.decode(token)

        def test_should_raise_invalid_access_token_exception_when_token_was_tampered_with(
            self, token_decode_outbound: PyJWTTokenDecodeOutboundAdapter
        ) -> None:
            token_value = encode_raw_token(make_claims())
            header, payload, signature = token_value.split(".")
            tampered_token = AccessTokenVO(f"{header}.{payload}x.{signature}")

            with pytest.raises(InvalidAccessTokenException):
                token_decode_outbound.decode(tampered_token)
