from dataclasses import FrozenInstanceError

import pytest
from faker import Faker

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestUserEntity:
    def test_should_create_user_entity_when_valid_data_is_provided(
        self, faker: Faker
    ) -> None:
        name = NameVO(faker.name())
        email = EmailVO(faker.email())
        password = PasswordHashVO(faker.text(max_nb_chars=255))
        role = UserRoleEnum.MEMBER

        user = UserEntity.create(name=name, email=email, password=password, role=role)

        assert user.id is not None
        assert user.name == name
        assert user.email == email
        assert user.password == password
        assert user.role == role
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_should_return_correct_types_for_user_entity_attributes(
        self, faker: Faker
    ) -> None:
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(faker.text(max_nb_chars=255)),
            role=UserRoleEnum.MEMBER,
        )

        assert isinstance(user.name, NameVO)
        assert isinstance(user.email, EmailVO)
        assert isinstance(user.password, PasswordHashVO)
        assert isinstance(user.role, UserRoleEnum)

    def test_should_raise_exception_when_attempting_to_modify_user_entity_email(
        self, faker: Faker
    ) -> None:
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(faker.text(max_nb_chars=255)),
            role=UserRoleEnum.MEMBER,
        )

        with pytest.raises(FrozenInstanceError):
            user.email = EmailVO(faker.email())  # type: ignore[misc]

    def test_should_return_equal_user_entities_when_data_is_identical(
        self, faker: Faker
    ) -> None:
        name = NameVO(faker.name())
        email = EmailVO(faker.email())
        password = PasswordHashVO(faker.text(max_nb_chars=255))

        user1 = UserEntity.create(name, email, password, UserRoleEnum.MEMBER)
        user2 = UserEntity(
            id=user1.id,
            name=name,
            email=email,
            password=password,
            role=UserRoleEnum.MEMBER,
            created_at=user1.created_at,
            updated_at=user1.updated_at,
        )

        assert user1 == user2
