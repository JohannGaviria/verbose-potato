import pytest
from faker import Faker


@pytest.fixture
def faker() -> Faker:
    return Faker()


def _generate_isbn13(faker: Faker) -> str:
    """Generate a random, check-digit-valid ISBN-13 string."""
    digits = [int(d) for d in faker.numerify("############")]
    total = sum(d if i % 2 == 0 else d * 3 for i, d in enumerate(digits))
    check_digit = (10 - (total % 10)) % 10
    return "".join(str(d) for d in digits) + str(check_digit)
