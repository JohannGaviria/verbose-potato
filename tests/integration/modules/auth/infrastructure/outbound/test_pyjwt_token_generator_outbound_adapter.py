from datetime import UTC, datetime
from uuid import UUID, uuid4

import jwt
import pytest

from src.config import settings
from src.modules.auth.domain.value_objects.access_token_claims_vo import (
    AccessTokenClaimsVO,
)
from src.modules.auth.domain.value_objects.access_token_result_vo import (
    AccessTokenResultVO,
)
from src.modules.auth.domain.value_objects.access_token_vo import AccessTokenVO
from src.modules.auth.infrastructure.outbound.pyjwt_token_generator_outbound_adapter import (
    PyJWTTokenGeneratorOutboundAdapter,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum

EXPIRATION_TOLERANCE_SECONDS = 5


class TestPyJWTTokenGeneratorOutboundAdapter:
    class TestGenerateAccess:
        def test_should_return_access_token_result_when_claims_are_valid(
            self, token_generator_outbound: PyJWTTokenGeneratorOutboundAdapter
        ) -> None:
            claims = AccessTokenClaimsVO(sub=uuid4(), role=UserRoleEnum.MEMBER)

            result = token_generator_outbound.generate_access(claims)

            assert isinstance(result, AccessTokenResultVO)
            assert isinstance(result.access_token, AccessTokenVO)
            assert result.token_type == "Bearer"
            assert result.expires_in == settings.JWT_ACCESS_TOKEN_EXPIRES_IN

        def test_should_generate_a_token_decodable_with_the_configured_secret(
            self, token_generator_outbound: PyJWTTokenGeneratorOutboundAdapter
        ) -> None:
            sub = uuid4()
            claims = AccessTokenClaimsVO(sub=sub, role=UserRoleEnum.LIBRARIAN)

            result = token_generator_outbound.generate_access(claims)

            decoded = jwt.decode(
                result.access_token.value,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )

            assert UUID(decoded["jti"])
            assert decoded["sub"] == str(sub)
            assert decoded["role"] == UserRoleEnum.LIBRARIAN.value

        def test_should_set_expiration_based_on_configured_expires_in(
            self, token_generator_outbound: PyJWTTokenGeneratorOutboundAdapter
        ) -> None:
            claims = AccessTokenClaimsVO(sub=uuid4(), role=UserRoleEnum.MEMBER)
            before = datetime.now(UTC)

            result = token_generator_outbound.generate_access(claims)

            decoded = jwt.decode(
                result.access_token.value,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            expected_exp = before.timestamp() + settings.JWT_ACCESS_TOKEN_EXPIRES_IN

            assert abs(decoded["exp"] - expected_exp) <= EXPIRATION_TOLERANCE_SECONDS

        def test_should_generate_a_unique_jti_for_each_call(
            self, token_generator_outbound: PyJWTTokenGeneratorOutboundAdapter
        ) -> None:
            claims = AccessTokenClaimsVO(sub=uuid4(), role=UserRoleEnum.MEMBER)

            first_result = token_generator_outbound.generate_access(claims)
            second_result = token_generator_outbound.generate_access(claims)

            first_decoded = jwt.decode(
                first_result.access_token.value,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            second_decoded = jwt.decode(
                second_result.access_token.value,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )

            assert first_decoded["jti"] != second_decoded["jti"]

        def test_should_generate_a_token_that_fails_verification_with_wrong_secret(
            self, token_generator_outbound: PyJWTTokenGeneratorOutboundAdapter
        ) -> None:
            claims = AccessTokenClaimsVO(sub=uuid4(), role=UserRoleEnum.MEMBER)

            result = token_generator_outbound.generate_access(claims)

            with pytest.raises(jwt.InvalidSignatureError):
                jwt.decode(
                    result.access_token.value,
                    "a-completely-different-secret-key",
                    algorithms=[settings.JWT_ALGORITHM],
                )

        def test_should_generate_a_token_that_fails_verification_with_wrong_algorithm(
            self, token_generator_outbound: PyJWTTokenGeneratorOutboundAdapter
        ) -> None:
            claims = AccessTokenClaimsVO(sub=uuid4(), role=UserRoleEnum.MEMBER)

            result = token_generator_outbound.generate_access(claims)

            with pytest.raises(jwt.InvalidAlgorithmError):
                jwt.decode(
                    result.access_token.value,
                    settings.JWT_SECRET_KEY,
                    algorithms=["HS512"],
                )
