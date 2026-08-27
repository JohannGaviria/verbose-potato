"""This module contains the PyJWT token decode outbound adapter."""

from datetime import UTC, datetime
from uuid import UUID

import jwt

from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.authentication_authorization_exception import (
    ExpiredAccessTokenException,
    InvalidAccessTokenException,
    InvalidAccessTokenPayloadException,
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
        """Decodes and verifies the access token, returning its typed payload.

        Args:
            token (AccessTokenVO): The access token to be decoded.

        Returns:
            AccessTokenPayloadVO: The decoded access token payload.

        Raises:
            ExpiredAccessTokenException: If the token's signature has expired.
            InvalidAccessTokenException: If the token is malformed, has an
                invalid signature, is missing a required claim, or carries a
                claim that cannot be converted to its domain type.
        """
        try:
            payload = jwt.decode(
                token.value,
                self._jwt_secret_key,
                algorithms=[self._jwt_algorithm],
            )

            return AccessTokenPayloadVO(
                jti=UUID(payload["jti"]),
                sub=UUID(payload["sub"]),
                role=UserRoleEnum(payload["role"]),
                exp=datetime.fromtimestamp(payload["exp"], tz=UTC),
            )
        except jwt.ExpiredSignatureError as exc:
            raise ExpiredAccessTokenException() from exc
        except jwt.InvalidTokenError as exc:
            raise InvalidAccessTokenException(
                "The access token is invalid or malformed."
            ) from exc
        except KeyError as exc:
            raise InvalidAccessTokenException(
                f"The access token is missing the required claim: {exc}."
            ) from exc
        except (ValueError, InvalidAccessTokenPayloadException) as exc:
            raise InvalidAccessTokenException(
                "The access token contains an invalid claim value."
            ) from exc
