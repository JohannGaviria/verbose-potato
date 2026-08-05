"""This module contains the infrastructure composition."""

from src.config import settings
from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)
from src.modules.auth.infrastructure.outbound.pyjwt_token_generator_outbound_adapter import (
    PyJWTTokenGeneratorOutboundAdapter,
)
from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.shared.infrastructure.database.database import db
from src.shared.presentation.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
)


def get_password_hash_outbound() -> Argon2PasswordHashOutboundAdapter:
    """Get the Argon2PasswordHashOutboundAdapter instance.

    Returns:
        Argon2PasswordHashOutboundAdapter: The Argon2PasswordHashOutboundAdapter instance.
    """
    return Argon2PasswordHashOutboundAdapter(
        time_cost=settings.ARGON2_TIME_COST,
        memory_cost=settings.ARGON2_MEMORY_COST,
        parallelism=settings.ARGON2_PARALLELISM,
    )


def get_user_unit_of_work() -> SQLAlchemyUserUnitOfWorkAdapter:
    """Get the SQLAlchemyUserUnitOfWorkAdapter instance.

    Returns:
        SQLAlchemyUserUnitOfWorkAdapter: The SQLAlchemyUserUnitOfWorkAdapter instance.
    """
    return SQLAlchemyUserUnitOfWorkAdapter(
        session_factory=db.session_factory(),
        logger_factory_outbound=get_logger_factory_outbound(),
    )


def get_token_generator_outbound() -> PyJWTTokenGeneratorOutboundAdapter:
    """Get the PyJWTTokenGeneratorOutboundAdapter instance.

    Returns:
        PyJWTTokenGeneratorOutboundAdapter: The PyJWTTokenGeneratorOutboundAdapter instance.
    """
    return PyJWTTokenGeneratorOutboundAdapter(
        jwt_secret_key=settings.JWT_SECRET_KEY,
        jwt_algorithm=settings.JWT_ALGORITHM,
        jwt_access_token_expires_in=settings.JWT_ACCESS_TOKEN_EXPIRES_IN,
    )
