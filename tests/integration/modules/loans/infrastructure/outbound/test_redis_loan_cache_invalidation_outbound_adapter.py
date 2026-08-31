from uuid import uuid4

import pytest
from redis.asyncio import Redis

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
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.infrastructure.outbound.redis_cache_outbound_adapter import (
    RedisCacheOutboundAdapter,
)

pytestmark = pytest.mark.db


@pytest.fixture
def adapter(
    redis_conn: Redis,
    logger_factory_outbound: LoggerFactoryOutboundPort,
) -> RedisLoanCacheInvalidationOutboundAdapter:
    return RedisLoanCacheInvalidationOutboundAdapter(
        loan_catalog_cache_outbound=RedisCacheOutboundAdapter(
            redis_client=redis_conn,
            factory=LoanCatalogCacheValueVO.from_dict,
            logger_factory_outbound=logger_factory_outbound,
        ),
        member_loan_cache_outbound=RedisCacheOutboundAdapter(
            redis_client=redis_conn,
            factory=MemberLoanCacheValueVO.from_dict,
            logger_factory_outbound=logger_factory_outbound,
        ),
        book_catalog_cache_outbound=RedisCacheOutboundAdapter(
            redis_client=redis_conn,
            factory=BookCatalogCacheValueVO.from_dict,
            logger_factory_outbound=logger_factory_outbound,
        ),
    )


class TestRedisLoanCacheInvalidationOutboundAdapter:
    async def test_should_invalidate_all_loan_catalog_cache_variants(
        self,
        adapter: RedisLoanCacheInvalidationOutboundAdapter,
        redis_conn: Redis,
    ) -> None:
        """Should invalidate all loan catalog cache variants."""
        catalog_key = "cache:loans:catalog"

        catalog_keys = [
            "cache:loans:catalog:hash-1",
            "cache:loans:catalog:hash-2",
            "cache:loans:catalog:hash-3",
        ]

        unrelated_key = "cache:loans:other:hash-1"

        for key in catalog_keys + [catalog_key]:
            await redis_conn.set(key, '{"name": "catalog", "age": 1}')

        await redis_conn.set(unrelated_key, '{"name": "other", "age": 2}')

        await adapter.invalidate(uuid4())

        for key in catalog_keys + [catalog_key]:
            assert await redis_conn.exists(key) == 0

        assert await redis_conn.exists(unrelated_key) == 1

        await redis_conn.delete(unrelated_key)

    async def test_should_invalidate_member_loan_cache_only_for_the_given_member(
        self,
        adapter: RedisLoanCacheInvalidationOutboundAdapter,
        redis_conn: Redis,
    ) -> None:
        """Should not remove another member's loan cache entries."""
        member_id = uuid4()
        other_member_id = uuid4()

        member_keys = [
            f"cache:loans:member:{member_id}:hash-1",
            f"cache:loans:member:{member_id}:hash-2",
            f"cache:loans:member:{member_id}",
        ]

        other_member_key = f"cache:loans:member:{other_member_id}:hash-1"

        for key in member_keys:
            await redis_conn.set(key, '{"name": "member", "age": 1}')

        await redis_conn.set(other_member_key, '{"name": "member", "age": 2}')

        await adapter.invalidate(member_id)

        for key in member_keys:
            assert await redis_conn.exists(key) == 0

        assert await redis_conn.exists(other_member_key) == 1

        await redis_conn.delete(other_member_key)

    async def test_should_invalidate_all_book_catalog_cache_variants(
        self,
        adapter: RedisLoanCacheInvalidationOutboundAdapter,
        redis_conn: Redis,
    ) -> None:
        """Should invalidate all book catalog cache variants."""
        catalog_key = "cache:books:catalog"

        catalog_keys = [
            "cache:books:catalog:hash-1",
            "cache:books:catalog:hash-2",
            "cache:books:catalog:hash-3",
        ]

        unrelated_key = "cache:books:other:hash-1"

        for key in catalog_keys + [catalog_key]:
            await redis_conn.set(key, '{"name": "catalog", "age": 1}')

        await redis_conn.set(unrelated_key, '{"name": "other", "age": 2}')

        await adapter.invalidate(uuid4())

        for key in catalog_keys + [catalog_key]:
            assert await redis_conn.exists(key) == 0

        assert await redis_conn.exists(unrelated_key) == 1

        await redis_conn.delete(unrelated_key)

    async def test_should_invalidate_all_caches_when_invalidate_is_called(
        self,
        adapter: RedisLoanCacheInvalidationOutboundAdapter,
        redis_conn: Redis,
    ) -> None:
        """Should remove loan catalog, member loan, and book catalog entries."""
        member_id = uuid4()

        loan_catalog_keys = [
            "cache:loans:catalog",
            "cache:loans:catalog:hash-1",
        ]
        member_keys = [
            f"cache:loans:member:{member_id}",
            f"cache:loans:member:{member_id}:hash-1",
        ]
        book_catalog_keys = [
            "cache:books:catalog",
            "cache:books:catalog:hash-1",
        ]

        for key in loan_catalog_keys + member_keys + book_catalog_keys:
            await redis_conn.set(key, '{"name": "cached", "age": 1}')

        await adapter.invalidate(member_id)

        for key in loan_catalog_keys + member_keys + book_catalog_keys:
            assert await redis_conn.exists(key) == 0

    async def test_should_not_raise_when_invalidate_is_called_on_missing_caches(
        self,
        adapter: RedisLoanCacheInvalidationOutboundAdapter,
    ) -> None:
        await adapter.invalidate(uuid4())
