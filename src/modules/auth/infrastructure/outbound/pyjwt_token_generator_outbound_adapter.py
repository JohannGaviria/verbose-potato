"""This module contains the PyJWT token generator outbound adapter."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from src.modules.auth.domain.ports.outbound.token_generator_outbound_port import (
    TokenGeneratorOutboundPort,
)
from src.modules.auth.domain.value_objects.access_token_claims_vo import (
    AccessTokenClaimsVO,
)
from src.modules.auth.domain.value_objects.access_token_payload_vo import (
    AccessTokenPayloadVO,
)
from src.modules.auth.domain.value_objects.access_token_result_vo import (
    AccessTokenResultVO,
)
from src.modules.auth.domain.value_objects.access_token_vo import AccessTokenVO


class PyJWTTokenGeneratorOutboundAdapter(TokenGeneratorOutboundPort):
    """Adapter used to generate tokens using the PyJWT algorithm."""

    def __init__(
        self,
        jwt_secret_key: str,
        jwt_algorithm: str,
        jwt_access_token_expires_in: int,
    ) -> None:
        """Initialize the PyJWTTokenGeneratorOutboundAdapter.

        Args:
            jwt_secret_key (str): The secret key used to sign the JWT.
            jwt_algorithm (str): The algorithm used to sign the JWT.
            jwt_access_token_expires_in (int): The number of seconds until the access token expires.
        """
        self._jwt_secret_key = jwt_secret_key
        self._jwt_algorithm = jwt_algorithm
        self._jwt_access_token_expires_in = jwt_access_token_expires_in

    def generate_access(self, claims: AccessTokenClaimsVO) -> AccessTokenResultVO:
        """Generates an access token.

        Args:
            claims (AccessTokenClaimsVO): The claims to be included in the access token.

        Returns:
            AccessTokenResultVO: The generated access token.
        """
        payload = AccessTokenPayloadVO(
            jti=uuid4(),
            sub=claims.sub,
            role=claims.role,
            exp=datetime.now(UTC)
            + timedelta(seconds=self._jwt_access_token_expires_in),
        )

        access_token = jwt.encode(
            payload.to_dict(), self._jwt_secret_key, self._jwt_algorithm
        )
        return AccessTokenResultVO(
            access_token=AccessTokenVO(access_token),
            token_type="Bearer",
            expires_in=self._jwt_access_token_expires_in,
        )
