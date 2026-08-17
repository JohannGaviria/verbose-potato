"""This module contains the infrastructure composition."""

from src.modules.books.infrastructure.persistence.unit_of_work.sqlalchemy_book_unit_of_work_adapter import (
    SQLAlchemyBookUnitOfWorkAdapter,
)
from src.shared.domain.ports.outbound.cache_outbound_port import CacheOutboundPort
from src.shared.domain.value_objects.cache_value_vo import CacheValueVO
from src.shared.infrastructure.cache.redis_client import redis_client
from src.shared.infrastructure.database.database import db
from src.shared.infrastructure.outbound.redis_cache_outbound_adapter import (
    RedisCacheOutboundAdapter,
)
from src.shared.presentation.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
)


def get_book_unit_of_work() -> SQLAlchemyBookUnitOfWorkAdapter:
    """Get the SQLAlchemyBookUnitOfWorkAdapter instance.

    Returns:
        SQLAlchemyBookUnitOfWorkAdapter: The SQLAlchemyBookUnitOfWorkAdapter instance.
    """
    return SQLAlchemyBookUnitOfWorkAdapter(
        session_factory=db.session_factory(),
        logger_factory_outbound=get_logger_factory_outbound(),
    )


def _book_catalog_cache_value_factory(data: dict) -> CacheValueVO:
    """Placeholder factory for the book catalog cache value.

    TODO: the registration new book use case only invalidates
        (deletes) the book catalog cache entry, it never reads or writes one, so
        this factory is never actually invoked. It will be replaced once the
        book catalog listing use case introduces a concrete cache value VO.

    Args:
        data (dict): The raw cached data.

    Raises:
        NotImplementedError: Always, until a concrete book catalog cache
            value VO exists.
    """
    raise NotImplementedError(
        "Book catalog cache retrieval is not implemented yet; only cache "
        "invalidation (delete) is used by the registration new book use case."
    )


def get_book_cache_outbound() -> CacheOutboundPort[CacheValueVO]:
    """Get the CacheOutboundPort instance used for the book catalog cache.

    Returns:
        CacheOutboundPort[CacheValueVO]: The book catalog cache outbound port instance.
    """
    return RedisCacheOutboundAdapter[CacheValueVO](
        redis_client=redis_client.client,
        factory=_book_catalog_cache_value_factory,
        logger_factory_outbound=get_logger_factory_outbound(),
    )
