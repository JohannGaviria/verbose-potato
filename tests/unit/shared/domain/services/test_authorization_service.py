from uuid import uuid4

import pytest

from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.authentication_authorization_exception import (
    InsufficientPermissionsException,
)
from src.shared.domain.services.authorization_service import AuthorizationService


@pytest.fixture
def authorization_service() -> AuthorizationService:
    return AuthorizationService()


class TestAuthorizationService:
    class TestAssertRole:
        @pytest.mark.parametrize("role", list(UserRoleEnum))
        def test_should_not_raise_when_user_role_matches_required_role(
            self, authorization_service: AuthorizationService, role: UserRoleEnum
        ) -> None:
            authorization_service.assert_role(user_role=role, required_role=role)

        def test_should_raise_insufficient_permissions_exception_when_user_role_does_not_match_required_role(
            self, authorization_service: AuthorizationService
        ) -> None:
            with pytest.raises(InsufficientPermissionsException):
                authorization_service.assert_role(
                    user_role=UserRoleEnum.MEMBER,
                    required_role=UserRoleEnum.LIBRARIAN,
                )

        def test_should_set_error_message_when_user_role_does_not_match_required_role(
            self, authorization_service: AuthorizationService
        ) -> None:
            with pytest.raises(InsufficientPermissionsException) as exc_info:
                authorization_service.assert_role(
                    user_role=UserRoleEnum.MEMBER,
                    required_role=UserRoleEnum.LIBRARIAN,
                )

            assert exc_info.value.error == (
                "The user does not have the required role to perform this action."
            )

        def test_should_raise_when_user_role_is_librarian_but_member_is_required(
            self, authorization_service: AuthorizationService
        ) -> None:
            with pytest.raises(InsufficientPermissionsException):
                authorization_service.assert_role(
                    user_role=UserRoleEnum.LIBRARIAN,
                    required_role=UserRoleEnum.MEMBER,
                )

    class TestAssertOwnership:
        def test_should_not_raise_when_user_is_the_resource_owner(
            self, authorization_service: AuthorizationService
        ) -> None:
            user_id = uuid4()

            authorization_service.assert_ownership(
                resource_owner_id=user_id,
                user_id=user_id,
            )

        def test_should_raise_insufficient_permissions_exception_when_user_is_not_the_resource_owner(
            self, authorization_service: AuthorizationService
        ) -> None:
            with pytest.raises(InsufficientPermissionsException):
                authorization_service.assert_ownership(
                    resource_owner_id=uuid4(),
                    user_id=uuid4(),
                )

        def test_should_set_error_message_when_user_is_not_the_resource_owner(
            self, authorization_service: AuthorizationService
        ) -> None:
            with pytest.raises(InsufficientPermissionsException) as exc_info:
                authorization_service.assert_ownership(
                    resource_owner_id=uuid4(),
                    user_id=uuid4(),
                )

            assert exc_info.value.error == (
                "The user does not have permission to access this resource."
            )
