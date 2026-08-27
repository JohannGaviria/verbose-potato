from dataclasses import dataclass

import pytest
from faker import Faker
from redis.asyncio import Redis

from src.shared.domain.exceptions.cache_exception import (
    CacheDeletionException,
    CacheRetrievalException,
    CacheStorageException,
)
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO
from src.shared.domain.value_objects.cache_value_vo import CacheValueVO
from src.shared.infrastructure.outbound.redis_cache_outbound_adapter import (
    RedisCacheOutboundAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)

pytestmark = pytest.mark.db


@dataclass(frozen=True, slots=True)
class DummyCacheValueVO(CacheValueVO):
    """Minimal concrete CacheValueVO used to exercise the adapter."""

    name: str
    age: int

    def to_dict(self) -> dict:
        return {"name": self.name, "age": self.age}


@dataclass(frozen=True, slots=True)
class UnserializableCacheValueVO(CacheValueVO):
    """A value whose to_dict() returns data json.dumps cannot serialize."""

    def to_dict(self) -> dict:
        # A set is not JSON-serializable, so json.dumps raises TypeError.
        return {"tags": {"a", "b"}}


@dataclass(frozen=True, slots=True)
class BrokenCacheValueVO(CacheValueVO):
    """A value whose to_dict() itself is buggy and raises unexpectedly."""

    def to_dict(self) -> dict:
        raise RuntimeError("to_dict is broken.")


def dummy_factory(data: dict) -> DummyCacheValueVO:
    return DummyCacheValueVO(name=data["name"], age=data["age"])


def broken_factory(data: dict) -> DummyCacheValueVO:
    raise RuntimeError("factory is broken.")


@pytest.fixture
def cache_key_prefix() -> str:
    """A unique-enough key segment so parallel test runs don't collide."""
    import uuid

    return uuid.uuid4().hex[:12]


class RedisClientWithoutInterface:
    """Stand-in dependency that doesn't implement the Redis client interface.

    Used only to prove the adapter's catch-all ``except Exception`` branch
    (an unexpected, non-Redis error) actually translates to the domain
    exception. This isn't mocking Redis' behavior — it's simulating a
    wiring/DI mistake, which is a realistic way to trigger an error that
    real Redis itself won't ever raise (Redis errors are always
    ``RedisError`` subclasses).
    """


@pytest.fixture
def adapter(
    redis_conn: Redis,
) -> RedisCacheOutboundAdapter[DummyCacheValueVO]:
    return RedisCacheOutboundAdapter(
        redis_client=redis_conn,
        factory=dummy_factory,
        logger_factory_outbound=StructlogLoggerFactoryOutboundAdapter(),
    )


class TestRedisCacheOutboundAdapter:
    async def test_should_return_none_when_key_is_not_cached(
        self,
        adapter: RedisCacheOutboundAdapter[DummyCacheValueVO],
        cache_key_prefix: str,
    ) -> None:
        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")

        result = await adapter.get(key)

        assert result is None

    async def test_should_store_and_retrieve_value_when_set_then_get(
        self,
        faker: Faker,
        adapter: RedisCacheOutboundAdapter[DummyCacheValueVO],
        cache_key_prefix: str,
    ) -> None:
        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")
        value = DummyCacheValueVO(name=faker.name(), age=faker.random_int())
        entry = CacheEntryVO(key=key, ttl=CacheTTLVO(seconds=60), value=value)

        await adapter.set(entry)
        result = await adapter.get(key)

        assert result == value

        await adapter.delete(key)

    async def test_should_store_entry_under_the_plain_key_value_not_its_repr(
        self,
        faker: Faker,
        adapter: RedisCacheOutboundAdapter[DummyCacheValueVO],
        redis_conn: Redis,
        cache_key_prefix: str,
    ) -> None:
        """Regression test.

        The adapter must use ``key.value()`` (the plain "cache:type:id" string)
        as the Redis key name. Using ``str(key)``/``str(entry.key)`` instead
        stores the entry under the dataclass ``repr()``
        (e.g. "CacheKeyVO(key='cache:test:...')"), which is never readable
        back through ``key.value()`` and breaks ``SCAN``/``KEYS`` pattern
        matching against the documented ``cache:{type}:{id}`` format.
        """
        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")
        value = DummyCacheValueVO(name=faker.name(), age=faker.random_int())
        entry = CacheEntryVO(key=key, ttl=CacheTTLVO(seconds=60), value=value)

        await adapter.set(entry)

        assert await redis_conn.exists(key.value()) == 1
        assert await redis_conn.exists(str(key)) == 0

        await adapter.delete(key)

    async def test_should_apply_ttl_when_set_is_called(
        self,
        faker: Faker,
        adapter: RedisCacheOutboundAdapter[DummyCacheValueVO],
        redis_conn: Redis,
        cache_key_prefix: str,
    ) -> None:
        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")
        value = DummyCacheValueVO(name=faker.name(), age=faker.random_int())
        entry = CacheEntryVO(key=key, ttl=CacheTTLVO(seconds=120), value=value)

        await adapter.set(entry)
        ttl = await redis_conn.ttl(key.value())

        assert 0 < ttl <= 120

        await adapter.delete(key)

    async def test_should_overwrite_value_when_set_is_called_with_same_key(
        self,
        faker: Faker,
        adapter: RedisCacheOutboundAdapter[DummyCacheValueVO],
        cache_key_prefix: str,
    ) -> None:
        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")
        first_value = DummyCacheValueVO(name=faker.name(), age=faker.random_int())
        second_value = DummyCacheValueVO(name=faker.name(), age=faker.random_int())

        await adapter.set(
            CacheEntryVO(key=key, ttl=CacheTTLVO(seconds=60), value=first_value)
        )
        await adapter.set(
            CacheEntryVO(key=key, ttl=CacheTTLVO(seconds=60), value=second_value)
        )

        result = await adapter.get(key)

        assert result == second_value

        await adapter.delete(key)

    async def test_should_remove_value_when_delete_is_called(
        self,
        faker: Faker,
        adapter: RedisCacheOutboundAdapter[DummyCacheValueVO],
        cache_key_prefix: str,
    ) -> None:
        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")
        value = DummyCacheValueVO(name=faker.name(), age=faker.random_int())

        await adapter.set(
            CacheEntryVO(
                key=key,
                ttl=CacheTTLVO(seconds=60),
                value=value,
            )
        )

        await adapter.delete(key)

        result = await adapter.get(key)

        assert result is None

    async def test_should_remove_exact_key_and_nested_keys_when_delete_is_called(
        self,
        faker: Faker,
        adapter: RedisCacheOutboundAdapter[DummyCacheValueVO],
        redis_conn: Redis,
        cache_key_prefix: str,
    ) -> None:
        """Should delete the exact key and all keys under its namespace."""
        prefix = f"cache:test:{cache_key_prefix}"
        key = CacheKeyVO(key=prefix)

        nested_keys = [
            CacheKeyVO(key=f"{prefix}:first"),
            CacheKeyVO(key=f"{prefix}:second"),
            CacheKeyVO(key=f"{prefix}:third"),
        ]

        value = DummyCacheValueVO(
            name=faker.name(),
            age=faker.random_int(),
        )

        await adapter.set(
            CacheEntryVO(
                key=key,
                ttl=CacheTTLVO(seconds=60),
                value=value,
            )
        )

        for nested_key in nested_keys:
            await redis_conn.set(
                nested_key.value(),
                '{"name": "nested", "age": 1}',
            )

        assert await redis_conn.exists(key.value()) == 1

        for nested_key in nested_keys:
            assert await redis_conn.exists(nested_key.value()) == 1

        await adapter.delete(key)

        assert await redis_conn.exists(key.value()) == 0

        for nested_key in nested_keys:
            assert await redis_conn.exists(nested_key.value()) == 0

    async def test_should_remove_only_matching_nested_keys_when_delete_is_called(
        self,
        adapter: RedisCacheOutboundAdapter[DummyCacheValueVO],
        redis_conn: Redis,
        cache_key_prefix: str,
    ) -> None:
        """Should not delete keys outside the requested namespace."""
        prefix = f"cache:test:{cache_key_prefix}"
        key = CacheKeyVO(key=prefix)

        matching_keys = [
            f"{prefix}:first",
            f"{prefix}:second",
            f"{prefix}:third",
        ]

        non_matching_key = f"cache:other:{cache_key_prefix}:first"

        for nested_key in matching_keys:
            await redis_conn.set(
                nested_key,
                '{"name": "nested", "age": 1}',
            )

        await redis_conn.set(
            non_matching_key,
            '{"name": "other", "age": 2}',
        )

        await adapter.delete(key)

        for nested_key in matching_keys:
            assert await redis_conn.exists(nested_key) == 0

        assert await redis_conn.exists(non_matching_key) == 1

        await redis_conn.delete(non_matching_key)

    async def test_should_remove_all_cache_entries_under_catalog_namespace(
        self,
        adapter: RedisCacheOutboundAdapter[DummyCacheValueVO],
        redis_conn: Redis,
    ) -> None:
        """Should invalidate all book catalog cache variants."""
        catalog_key = CacheKeyVO(key="cache:books:catalog")

        catalog_keys = [
            "cache:books:catalog:hash-1",
            "cache:books:catalog:hash-2",
            "cache:books:catalog:hash-3",
        ]

        unrelated_key = "cache:books:other:hash-1"

        for cache_key in catalog_keys:
            await redis_conn.set(
                cache_key,
                '{"name": "catalog", "age": 1}',
            )

        await redis_conn.set(
            unrelated_key,
            '{"name": "other", "age": 2}',
        )

        await adapter.delete(catalog_key)

        for cache_key in catalog_keys:
            assert await redis_conn.exists(cache_key) == 0

        assert await redis_conn.exists(unrelated_key) == 1

        await redis_conn.delete(unrelated_key)

    async def test_should_not_raise_when_delete_is_called_on_missing_key(
        self,
        adapter: RedisCacheOutboundAdapter[DummyCacheValueVO],
        cache_key_prefix: str,
    ) -> None:
        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")

        await adapter.delete(key)

    async def test_should_raise_cache_retrieval_exception_when_cached_value_is_not_json(
        self,
        adapter: RedisCacheOutboundAdapter[DummyCacheValueVO],
        redis_conn: Redis,
        cache_key_prefix: str,
    ) -> None:
        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")

        # Write malformed data directly, bypassing the adapter, to simulate
        # cache corruption.
        await redis_conn.set(key.value(), "not-valid-json")

        with pytest.raises(CacheRetrievalException):
            await adapter.get(key)

        await redis_conn.delete(key.value())

    async def test_should_raise_cache_retrieval_exception_when_redis_is_unreachable(
        self,
        cache_key_prefix: str,
    ) -> None:
        broken_client: Redis = Redis.from_url(
            "redis://127.0.0.1:1",
            socket_connect_timeout=1,
            socket_timeout=1,
        )

        broken_adapter = RedisCacheOutboundAdapter(
            redis_client=broken_client,
            factory=dummy_factory,
            logger_factory_outbound=StructlogLoggerFactoryOutboundAdapter(),
        )

        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")

        with pytest.raises(CacheRetrievalException):
            await broken_adapter.get(key)

        await broken_client.aclose()

    async def test_should_raise_cache_storage_exception_when_redis_is_unreachable(
        self,
        faker: Faker,
        cache_key_prefix: str,
    ) -> None:
        broken_client: Redis = Redis.from_url(
            "redis://127.0.0.1:1",
            socket_connect_timeout=1,
            socket_timeout=1,
        )

        broken_adapter = RedisCacheOutboundAdapter(
            redis_client=broken_client,
            factory=dummy_factory,
            logger_factory_outbound=StructlogLoggerFactoryOutboundAdapter(),
        )

        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")
        value = DummyCacheValueVO(
            name=faker.name(),
            age=faker.random_int(),
        )

        entry = CacheEntryVO(
            key=key,
            ttl=CacheTTLVO(seconds=60),
            value=value,
        )

        with pytest.raises(CacheStorageException):
            await broken_adapter.set(entry)

        await broken_client.aclose()

    async def test_should_raise_cache_deletion_exception_when_redis_is_unreachable(
        self,
        cache_key_prefix: str,
    ) -> None:
        broken_client: Redis = Redis.from_url(
            "redis://127.0.0.1:1",
            socket_connect_timeout=1,
            socket_timeout=1,
        )

        broken_adapter = RedisCacheOutboundAdapter(
            redis_client=broken_client,
            factory=dummy_factory,
            logger_factory_outbound=StructlogLoggerFactoryOutboundAdapter(),
        )

        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")

        with pytest.raises(CacheDeletionException):
            await broken_adapter.delete(key)

        await broken_client.aclose()

    async def test_should_raise_cache_storage_exception_when_value_is_not_json_serializable(
        self,
        redis_conn: Redis,
        cache_key_prefix: str,
    ) -> None:
        adapter: RedisCacheOutboundAdapter[UnserializableCacheValueVO] = (
            RedisCacheOutboundAdapter(
                redis_client=redis_conn,
                factory=lambda data: UnserializableCacheValueVO(),
                logger_factory_outbound=StructlogLoggerFactoryOutboundAdapter(),
            )
        )

        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")

        entry = CacheEntryVO(
            key=key,
            ttl=CacheTTLVO(seconds=60),
            value=UnserializableCacheValueVO(),
        )

        with pytest.raises(CacheStorageException):
            await adapter.set(entry)

    async def test_should_raise_cache_storage_exception_when_to_dict_raises_unexpectedly(
        self,
        redis_conn: Redis,
        cache_key_prefix: str,
    ) -> None:
        adapter: RedisCacheOutboundAdapter[BrokenCacheValueVO] = (
            RedisCacheOutboundAdapter(
                redis_client=redis_conn,
                factory=lambda data: BrokenCacheValueVO(),
                logger_factory_outbound=StructlogLoggerFactoryOutboundAdapter(),
            )
        )

        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")

        entry = CacheEntryVO(
            key=key,
            ttl=CacheTTLVO(seconds=60),
            value=BrokenCacheValueVO(),
        )

        with pytest.raises(CacheStorageException):
            await adapter.set(entry)

    async def test_should_raise_cache_retrieval_exception_when_factory_raises_unexpectedly(
        self,
        faker: Faker,
        redis_conn: Redis,
        cache_key_prefix: str,
    ) -> None:
        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")

        # Store a well-formed entry with the working adapter first, so the
        # Redis get() and json.loads() calls both succeed for real.
        working_adapter: RedisCacheOutboundAdapter[DummyCacheValueVO] = (
            RedisCacheOutboundAdapter(
                redis_client=redis_conn,
                factory=dummy_factory,
                logger_factory_outbound=StructlogLoggerFactoryOutboundAdapter(),
            )
        )

        await working_adapter.set(
            CacheEntryVO(
                key=key,
                ttl=CacheTTLVO(seconds=60),
                value=DummyCacheValueVO(
                    name=faker.name(),
                    age=faker.random_int(),
                ),
            )
        )

        # Only the reconstruction step (self._factory(data)) fails.
        broken_adapter: RedisCacheOutboundAdapter[DummyCacheValueVO] = (
            RedisCacheOutboundAdapter(
                redis_client=redis_conn,
                factory=broken_factory,
                logger_factory_outbound=StructlogLoggerFactoryOutboundAdapter(),
            )
        )

        with pytest.raises(CacheRetrievalException):
            await broken_adapter.get(key)

        await redis_conn.delete(key.value())

    async def test_should_raise_cache_deletion_exception_when_unexpected_error_occurs(
        self,
        cache_key_prefix: str,
    ) -> None:
        broken_adapter: RedisCacheOutboundAdapter[DummyCacheValueVO] = (
            RedisCacheOutboundAdapter(
                redis_client=RedisClientWithoutInterface(),  # type: ignore[arg-type]
                factory=dummy_factory,
                logger_factory_outbound=StructlogLoggerFactoryOutboundAdapter(),
            )
        )

        key = CacheKeyVO(key=f"cache:test:{cache_key_prefix}")

        with pytest.raises(CacheDeletionException):
            await broken_adapter.delete(key)
