from faker import Faker

from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)


class TestArgon2PasswordHashOutboundAdapter:
    class TestHash:
        def test_should_return_password_hash_when_plain_password_is_provided(
            self,
            faker: Faker,
            password_hash_outbound: Argon2PasswordHashOutboundAdapter,
        ) -> None:
            plain_password = PlainPasswordVO(faker.password())

            result = password_hash_outbound.hash(plain_password)

            assert isinstance(result, PasswordHashVO)
            assert result.password_hash is not None

        def test_should_return_different_hashes_when_same_plain_password_is_hashed_twice(
            self,
            faker: Faker,
            password_hash_outbound: Argon2PasswordHashOutboundAdapter,
        ) -> None:
            plain_password = PlainPasswordVO(faker.password())

            hash1 = password_hash_outbound.hash(plain_password)
            hash2 = password_hash_outbound.hash(plain_password)

            assert hash1.password_hash != hash2.password_hash
