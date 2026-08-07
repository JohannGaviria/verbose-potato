"""This module contains the token decode outbound port."""

from abc import ABC, abstractmethod

from src.shared.domain.value_objects.access_token_payload_vo import (
    AccessTokenPayloadVO,
)
from src.shared.domain.value_objects.access_token_vo import AccessTokenVO


class TokenDecodeOutboundPort(ABC):
    """Outbound port used to decode tokens."""

    @abstractmethod
    def decode(self, token: AccessTokenVO) -> AccessTokenPayloadVO:
        """Decodes the access token.

        Args:
            token (AccessTokenVO): The access token to be decoded.

        Returns:
            AccessTokenPayloadVO: The decoded access token payload.
        """
        pass
