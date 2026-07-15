# Testing Strategy - Verbose Potato

> Defines the project's testing strategy, specifying what is tested, how it is tested, and the purpose of each testing level to ensure the quality and correct operation of the system.
>

## Table of Contents

1. [Objective](#1-objective)
2. [Testing Pyramid](#2-testing-pyramid)
3. [Unit Tests](#3-unit-tests)
4. [Integration Tests](#4-integration-tests)
5. [End-to-End (E2E) Tests](#5-end-to-end-e2e-tests)
6. [Principles](#6-principles)
7. [Naming Convention](#7-naming-convention)
8. [Summary](#8-summary)

---

## 1. Objective

The testing strategy aims to ensure that the system is:

- **Correct**, validating that business rules behave as expected.
- **Reliable**, preventing regressions when adding new features.
- **Maintainable**, allowing safe refactoring.
- **Predictable**, verifying system behavior from different levels.

---

## 2. Testing Pyramid

The project follows the classic testing pyramid strategy.

```
        E2E
    Integration
      Unit
```

The largest number of tests corresponds to unit tests, followed by integration tests, and finally a smaller set of End-to-End tests to validate the main flows.

---

## 3. Unit Tests

### What is tested

- Entities.
- Value Objects.
- Use Cases.
- Business rules.

### How it is tested

- Without using PostgreSQL.
- Without using Redis.
- Without making HTTP calls.
- Using mocks for the domain ports.

### Objective

Validate business logic in a fast, isolated, and deterministic way.

---

## 4. Integration Tests

### What is tested

- Repositories.
- Port implementations.
- Persistence with PostgreSQL.
- Integration with Redis.

## How it is tested

- Real test database.
- Test Redis instance.
- No infrastructure mocks.

## Objective

Ensure that the infrastructure correctly implements the contracts defined by the domain.

---

# 5. End-to-End (E2E) Tests

## What is tested

The main functional flows of the system through the REST API.

For example:

- User registration.
- Login.
- Book registration.
- Loan registration.
- Return registration.
- Catalog lookup.

## How it is tested

- Real HTTP requests using `httpx`.
- Fully initialized API.
- Test database.
- Test Redis instance.

## Objective

Validate that all system components work correctly end to end.

---

# 6. Principles

The testing strategy follows these principles:

- Each test must validate a single behavior.
- Tests must be independent of one another.
- Tests must be deterministic.
- The system's behavior should be tested, not implementation details.
- Whenever possible, business rules must be covered by unit tests.

---

# 7. Naming Convention

## Methods

All test methods must follow the pattern:

```
test_should_<expected_behavior>_when_<condition>
```

Examples:

```python
test_should_create_book_when_data_is_valid()

test_should_return_conflict_when_isbn_already_exists()

test_should_register_loan_when_book_is_available()
```

## Classes

Test classes must have the same name as the class under test, preceded by `Test`.

```python
class TestBookEntity:
    ...

class TestCreateLoanUseCase:
    ...

class TestISBNVO:
    ...
```

## Files

Files must keep the same name as the original file, preceded by `test_`.

```
book_entity.py

↓

test_book_entity.py
```

---

# 8. Summary

| Type | Layer | Objective |
| --- | --- | --- |
| Unit | Domain and Application | Validate business rules |
| Integration | Infrastructure | Validate PostgreSQL, Redis, and repositories |
| End-to-End | Presentation | Validate the complete API flows |
