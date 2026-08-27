"""This module contains the security compositions."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, PyJWTError

from src.shared.domain.exceptions.authentication_authorization_exception import (
    AuthenticationTokenMissingException,
    ExpiredAccessTokenException,
    InvalidAccessTokenException,
)
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.domain.value_objects.access_token_vo import AccessTokenVO
from src.shared.infrastructure.outbound.pyjwt_toke_decode_outbound_adapter import (
    PyJWTTokenDecodeOutboundAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
    get_token_decode_outbound,
)

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    token_outbound: PyJWTTokenDecodeOutboundAdapter = Depends(
        get_token_decode_outbound
    ),
) -> AccessTokenPayloadVO:
    """Dependency injector to get the current user from the JWT token.

    Args:
        credentials (HTTPAuthorizationCredentials | None): The HTTP authorization credentials.
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): Factory used to create
            the logger instance.
        token_outbound (PyJWTTokenOutboundAdapter): Outbound used to decode the token.

    Returns:
        AccessTokenPayloadVO: The access token payload value object.

    Raises:
        AuthenticationTokenMissingException: If no authentication token is provided.
        ExpiredAccessTokenException: If the access token has expired.
        InvalidAccessTokenException: If the access token is invalid.
    """
    _logger = logger_factory_outbound.get_logger(__name__)

    if credentials is None:
        _logger.warning("Authentication failed because no access token was provided.")
        raise AuthenticationTokenMissingException()

    try:
        token = credentials.credentials
        payload = token_outbound.decode(AccessTokenVO(token))

        _logger.debug("Authentication succeeded.", user_id=payload.sub)

        return AccessTokenPayloadVO(
            jti=payload.jti, sub=payload.sub, role=payload.role, exp=payload.exp
        )

    except ExpiredSignatureError as exc:
        _logger.warning(
            "Authentication failed due to an expired token.", exc_info=str(exc)
        )
        raise ExpiredAccessTokenException() from exc
    except PyJWTError as exc:
        _logger.warning(
            "Authentication failed because the access token is invalid.",
            exc_info=str(exc),
        )
        raise InvalidAccessTokenException(
            "The access token is invalid or malformed."
        ) from exc
