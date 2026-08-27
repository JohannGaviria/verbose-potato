"""This module contains the infrastructure composition."""

from src.modules.books.domain.value_objects.book_catalog_cache_value_vo import (
    BookCatalogCacheValueVO,
)
from src.modules.books.infrastructure.persistence.unit_of_work.sqlalchemy_book_unit_of_work_adapter import (
    SQLAlchemyBookUnitOfWorkAdapter,
)
from src.shared.domain.ports.outbound.cache_outbound_port import CacheOutboundPort
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


def get_book_cache_outbound() -> CacheOutboundPort[BookCatalogCacheValueVO]:
    """Get the CacheOutboundPort instance used for the book catalog cache.

    Returns:
        CacheOutboundPort[BookCatalogCacheValueVO]: The book catalog cache outbound port instance.
    """
    return RedisCacheOutboundAdapter[BookCatalogCacheValueVO](
        redis_client=redis_client.client,
        factory=BookCatalogCacheValueVO.from_dict,
        logger_factory_outbound=get_logger_factory_outbound(),
    )
