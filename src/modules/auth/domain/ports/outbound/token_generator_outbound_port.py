"""This module contains the token generator outbound port."""

from abc import ABC, abstractmethod

from src.modules.auth.domain.value_objects.access_token_claims_vo import (
    AccessTokenClaimsVO,
)
from src.modules.auth.domain.value_objects.access_token_result_vo import (
    AccessTokenResultVO,
)


class TokenGeneratorOutboundPort(ABC):
    """Outbound port for generating tokens."""

    @abstractmethod
    def generate_access(self, claims: AccessTokenClaimsVO) -> AccessTokenResultVO:
        """Generates an access token.

        Args:
            claims (AccessTokenClaimsVO): The claims to be included in the access token.

        Returns:
            AccessTokenResultVO: The generated access token.
        """
        pass
