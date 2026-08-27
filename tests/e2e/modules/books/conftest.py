from collections.abc import Callable
from datetime import date
from typing import Any

import pytest
from faker import Faker

from tests.conftest import _generate_isbn13


@pytest.fixture
def register_book_payload(faker: Faker) -> Callable[[], dict[str, Any]]:
    """Factory for a valid book registration payload."""

    def _make() -> dict[str, Any]:
        return {
            "title": faker.sentence(nb_words=4),
            "isbn": _generate_isbn13(faker),
            "author": faker.name(),
            "published_year": faker.random_int(min=1450, max=date.today().year),
            "total_copies": faker.random_int(min=1, max=20),
        }

    return _make
