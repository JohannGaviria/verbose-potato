"""This module contains the PyJWT token decode outbound adapter."""

import jwt

from src.shared.domain.exceptions.authentication_authorization_exception import (
    ExpiredAccessTokenException,
    InvalidAccessTokenException,
)
from src.shared.domain.ports.outbound.token_decode_outbound_port import (
    TokenDecodeOutboundPort,
)
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.domain.value_objects.access_token_vo import AccessTokenVO


class PyJWTTokenDecodeOutboundAdapter(TokenDecodeOutboundPort):
    """Adapter used to decode tokens using the PyJWT algorithm."""

    def __init__(self, jwt_secret_key: str, jwt_algorithm: str) -> None:
        """Initialize the PyJWTTokenDecodeOutboundAdapter."""
        self._jwt_secret_key = jwt_secret_key
        self._jwt_algorithm = jwt_algorithm

    def decode(self, token: AccessTokenVO) -> AccessTokenPayloadVO:
        """."""
        try:
            payload = jwt.decode(
                token.value,
                self._jwt_secret_key,
                algorithms=[self._jwt_algorithm],
            )

            return AccessTokenPayloadVO(
                jti=payload["jti"],
                sub=payload["sub"],
                role=payload["role"],
                exp=payload["exp"],
            )
        except jwt.ExpiredSignatureError as exc:
            raise ExpiredAccessTokenException() from exc
        except jwt.InvalidTokenError as exc:
            raise InvalidAccessTokenException(
                "The access token is invalid or malformed."
            ) from exc
