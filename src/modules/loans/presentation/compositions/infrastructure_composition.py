"""This module contains the infrastructure composition."""

from src.modules.books.domain.value_objects.book_catalog_cache_value_vo import (
    BookCatalogCacheValueVO,
)
from src.modules.loans.domain.value_objects.loan_catalog_cache_value_vo import (
    LoanCatalogCacheValueVO,
)
from src.modules.loans.domain.value_objects.member_loan_cache_value_vo import (
    MemberLoanCacheValueVO,
)
from src.modules.loans.infrastructure.outbound.redis_loan_cache_invalidation_outbound_adapter import (
    RedisLoanCacheInvalidationOutboundAdapter,
)
from src.modules.loans.infrastructure.persistence.unit_of_work.sqlalchemy_loan_unit_of_work_adapter import (
    SQLAlchemyLoanUnitOfWorkAdapter,
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


def get_loan_catalog_cache_outbound() -> CacheOutboundPort[LoanCatalogCacheValueVO]:
    """Get the loan catalog cache outbound adapter instance.

    Returns:
        CacheOutboundPort[LoanCatalogCacheValueVO]: The loan catalog cache outbound adapter.
    """
    return RedisCacheOutboundAdapter[LoanCatalogCacheValueVO](
        redis_client=redis_client.client,
        factory=LoanCatalogCacheValueVO.from_dict,
        logger_factory_outbound=get_logger_factory_outbound(),
    )


def get_member_loan_cache_outbound() -> CacheOutboundPort[MemberLoanCacheValueVO]:
    """Get the member loan cache outbound adapter instance.

    Returns:
        CacheOutboundPort[MemberLoanCacheValueVO]: The member loan cache outbound adapter.
    """
    return RedisCacheOutboundAdapter[MemberLoanCacheValueVO](
        redis_client=redis_client.client,
        factory=MemberLoanCacheValueVO.from_dict,
        logger_factory_outbound=get_logger_factory_outbound(),
    )


def get_loan_unit_of_work() -> SQLAlchemyLoanUnitOfWorkAdapter:
    """Get the SQLAlchemyLoanUnitOfWorkAdapter instance.

    Returns:
        SQLAlchemyLoanUnitOfWorkAdapter: The SQLAlchemyLoanUnitOfWorkAdapter instance.
    """
    return SQLAlchemyLoanUnitOfWorkAdapter(
        session_factory=db.session_factory(),
        logger_factory_outbound=get_logger_factory_outbound(),
    )


def get_loan_cache_invalidation_outbound() -> RedisLoanCacheInvalidationOutboundAdapter:
    """Get the RedisLoanCacheInvalidationOutboundAdapter instance.

    Returns:
        RedisLoanCacheInvalidationOutboundAdapter: The RedisLoanCacheInvalidationOutboundAdapter instance.
    """
    return RedisLoanCacheInvalidationOutboundAdapter(
        loan_catalog_cache_outbound=get_loan_catalog_cache_outbound(),
        member_loan_cache_outbound=get_member_loan_cache_outbound(),
        book_catalog_cache_outbound=RedisCacheOutboundAdapter[BookCatalogCacheValueVO](
            redis_client=redis_client.client,
            factory=BookCatalogCacheValueVO.from_dict,
            logger_factory_outbound=get_logger_factory_outbound(),
        ),
    )
