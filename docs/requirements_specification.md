# Requirements Specification - Verbose Potato

> Defines the functionalities offered by the system, organized by module and expressed through functional requirements and their respective user stories, establishing the expected behavior of the application from a business perspective.

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Functional Requirements](#2-functional-requirements)
3. [User Stories](#3-user-stories)
4.  [Data Models](#4-data-models)

---

## 1. Project Overview

- **Project name:** Verbose Potato
- **Short description:** A REST API for managing a library, allowing administration of users, books, and loans through business rules that ensure copy availability and data consistency.
- **Detailed description:** Verbose Potato is a backend system designed to manage a library in a simple and secure way. The application allows registering users, managing the book catalog, and controlling the complete loan and return cycle.

    The domain focuses on applying business rules such as copy availability, the loan limit per user, prevention of duplicate loans, and data integrity when returning or deleting resources. The project aims to serve as a practical implementation of Hexagonal Architecture, keeping the domain completely decoupled from the technologies used in the infrastructure.

- **Actors involved:**
    - **Librarian:** manages users, books, and loans.
    - **Member:** represented within the system as the beneficiary of loans.
- **Architecture type:** Hexagonal Architecture (Ports & Adapters).
- **Internal architectural pattern:** Domain-oriented modular monolith, organized by functional modules and based on Use Cases (Application Layer), Entities, Value Objects, Ports, and Adapters.
- **Initial technology stack (tentative):**
    - **Language:** Python
    - **Framework:** FastApi
    - **Database:** PostgreSQL
    - **Others:** SQLAlchemy · Alembic · Redis · PyJWT · Argon2 · Structlog · Ruff · Mypy · Pytest · Pytest-Asyncio · Docker · Docker Compose · GitHub Actions

---

## 2. Functional Requirements

### Module 1: Authentication

- **FR-001:** The system must automatically create a first user with the `LIBRARIAN` role during application startup.
- **FR-002:** The system must allow anyone to register as a user with the `MEMBER` role.
- **FR-003:** The system must allow a registered user to log in using their credentials.

### Module 2: Book management

- **FR-004:** The system must allow a `LIBRARIAN` to register new books.
- **FR-005:** The system must allow a `LIBRARIAN` to update information for existing books.
- **FR-006:** The system must allow a `LIBRARIAN` to delete books.
- **FR-007:** The system must allow listing registered books.

### Module 3: Loan management

- **FR-008:** The system must allow a `MEMBER` to register a book loan.
- **FR-009:** The system must allow a `MEMBER` to register the return of one of their loans.
- **FR-010:** The system must allow a `MEMBER` to view their loans.
- **FR-011:** The system must allow a `LIBRARIAN` to view the loans of all users.

---

## 3. User Stories

### Module 1: Authentication

### US-FR-001: Automatic registration of the `LIBRARIAN` on application startup

**As** the System,

**I want** to automatically create the first user with the `LIBRARIAN` role during application startup, when no librarian is yet registered,

**So that** the platform has an administrator user from its very first run.

**Trigger:** Application startup (`create_first_librarian`)

**Acceptance criteria:**

- [ ]  The system must obtain the `name`, `email`, and `password` of the first `LIBRARIAN` from environment variables.
- [ ]  The `name` must not be empty and must be between 3 and 100 characters long.
- [ ]  The `email` must have a valid format and must not already be registered.
- [ ]  The `password` must be between 8 and 16 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character.
- [ ]  The `password` must be stored using Argon2.
- [ ]  If at least one user with the `LIBRARIAN` role already exists, the system must not create a new one.
- [ ]  The process must be idempotent; restarting the application must not generate multiple `LIBRARIAN` users.
- [ ]  The system must log successful and failed executions of the process.

### US-FR-002: Registration of new users

**As** a visitor,

**I want** to register by providing my credentials,

**So that** I can obtain an account and access the library's services.

**Endpoint:** `POST /api/v1/auth/register`

**Acceptance criteria:**

- [ ]  The user must provide a `name`, an `email`, and a `password`.
- [ ]  The `name` must not be empty and must be between 3 and 100 characters long.
- [ ]  The `email` must have a valid format and must not already be registered.
- [ ]  The `password` must be between 8 and 16 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character.
- [ ]  The `password` must be stored using Argon2.
- [ ]  The user must be automatically registered with the `MEMBER` role.
- [ ]  The system must log successful and failed executions of the process.
- [ ]  The endpoint returns the created user's data: `id`, `name`, `email`, `role`, `created_at`, `updated_at`.
- [ ]  Returns status `201 Created` if the user was registered successfully.
- [ ]  Returns status `400 Bad Request` if any field fails format validation.
- [ ]  Returns status `409 Conflict` if the email is already registered.
- [ ]  Returns status `422 Unprocessable Entity` if a required field is missing or malformed.
- [ ]  Returns status `500 Internal Server Error` if an unexpected error occurs.

### US-FR-003: Login

**As** a registered user,

**I want** to log in using my credentials,

**So that** I can access the system's functionalities according to my role.

**Endpoint:** `POST /api/v1/auth/login`

**Acceptance criteria:**

- [ ]  The user must provide their `email` and `password`.
- [ ]  The system must validate the provided credentials.
- [ ]  The system must generate a `JWT Access Token` when the credentials are valid.
- [ ]  The `Access Token` must contain the user's identifier and role.
- [ ]  If the credentials are invalid, the system must reject authentication without revealing which field is incorrect.
- [ ]  The system must log successful and failed executions of the process.
- [ ]  The endpoint returns the authenticated user's data and the token: `id`, `name`, `email`, `role`, `access_token`, `exp`.
- [ ]  Returns status `200 OK` if the user was authenticated successfully.
- [ ]  Returns status `400 Bad Request` if any field fails format validation.
- [ ]  Returns status `401 Unauthorized` if the credentials are invalid.
- [ ]  Returns status `422 Unprocessable Entity` if a required field is missing or malformed.
- [ ]  Returns status `500 Internal Server Error` if an unexpected error occurs.

### Module 2: Book management

### US-FR-004: Registration of new books

**As** a `LIBRARIAN`,

**I want** to register a new book,

**So that** I can expand the library's available catalog.

**Endpoint:** `POST /api/v1/books`

**Cache Strategy:** Invalidate `cache:books:catalog:{filters_hash}`

**Acceptance criteria:**

- [ ]  Only a user with the `LIBRARIAN` role can register new books.
- [ ]  The `LIBRARIAN` must provide the `title`, `isbn`, `author`, `published_year`, and `total_copies`.
- [ ]  When registering a book, `available_copies` must be initialized with the same value as `total_copies`.
- [ ]  The `title` must not be empty and must be between 3 and 255 characters long.
- [ ]  The `isbn` must have a valid format and must not already be registered.
- [ ]  The `author` must not be empty and must be between 3 and 100 characters long.
- [ ]  The `published_year` must be a valid year.
- [ ]  The `total_copies` must be an integer greater than or equal to 1.
- [ ]  The system must invalidate the book catalog cache after registering a new book.
- [ ]  The system must log successful and failed executions of the process.
- [ ]  The endpoint returns the created book's data: `id`, `title`, `isbn`, `author`, `published_year`, `total_copies`, `available_copies`, `created_at`, `updated_at`.
- [ ]  Returns status `201 Created` if the book was registered successfully.
- [ ]  Returns status `400 Bad Request` if any field fails format validation.
- [ ]  Returns status `401 Unauthorized` if the token is invalid or missing.
- [ ]  Returns status `403 Forbidden` if the authenticated user does not have the `LIBRARIAN` role.
- [ ]  Returns status `409 Conflict` if the ISBN is already registered.
- [ ]  Returns status `422 Unprocessable Entity` if a required field is missing or malformed.
- [ ]  Returns status `500 Internal Server Error` if an unexpected error occurs.

### US-FR-005: Updating books

**As** a `LIBRARIAN`,

**I want** to update the information of an existing book,

**So that** I can keep the library's catalog up to date.

**Endpoint:** `PATCH /api/v1/books/{book_id}`

**Cache Strategy:** Invalidate `cache:books:catalog:{filters_hash}`

**Acceptance criteria:**

- [ ]  Only a user with the `LIBRARIAN` role can update a book's information.
- [ ]  The `LIBRARIAN` must specify the book's identifier (`book_id`).
- [ ]  The system must verify that the book exists.
- [ ]  It must be possible to update the `title`, `author`, `published_year`, and `total_copies`.
- [ ]  The `title` must be between 3 and 255 characters long.
- [ ]  The `author` must be between 3 and 100 characters long.
- [ ]  The `published_year` must be a valid year.
- [ ]  `total_copies` cannot be less than the number of copies currently on loan.
- [ ]  The system must invalidate the book catalog cache after updating a book.
- [ ]  The system must log successful and failed executions of the process.
- [ ]  The endpoint returns the updated book's data: `id`, `title`, `isbn`, `author`, `published_year`, `total_copies`, `available_copies`, `created_at`, `updated_at`.
- [ ]  Returns status `200 OK` if the book was updated successfully.
- [ ]  Returns status `401 Unauthorized` if the token is invalid or missing.
- [ ]  Returns status `403 Forbidden` if the authenticated user does not have the `LIBRARIAN` role.
- [ ]  Returns status `404 Not Found` if the book does not exist.
- [ ]  Returns status `409 Conflict` if the update violates a business rule.
- [ ]  Returns status `422 Unprocessable Entity` if a required field is missing or malformed.
- [ ]  Returns status `500 Internal Server Error` if an unexpected error occurs.

### US-FR-006: Deleting books

**As** a `LIBRARIAN`,

**I want** to delete a book from the catalog,

**So that** I can keep the library's collection up to date.

**Endpoint:** `DELETE /api/v1/books/{book_id}`

**Cache Strategy:** Invalidate `cache:books:catalog:{filters_hash}`

**Acceptance criteria:**

- [ ]  Only a user with the `LIBRARIAN` role can delete a book.
- [ ]  The `LIBRARIAN` must specify the book's identifier (`book_id`).
- [ ]  The system must verify that the book exists.
- [ ]  The system must not allow deleting a book with active loans.
- [ ]  The system must invalidate the book catalog cache after deleting a book.
- [ ]  The system must log successful and failed executions of the process.
- [ ]  Returns status `204 No Content` if the book was deleted successfully.
- [ ]  Returns status `401 Unauthorized` if the token is invalid or missing.
- [ ]  Returns status `403 Forbidden` if the authenticated user does not have the `LIBRARIAN` role.
- [ ]  Returns status `404 Not Found` if the book does not exist.
- [ ]  Returns status `409 Conflict` if the book has active loans.
- [ ]  Returns status `500 Internal Server Error` if an unexpected error occurs.

### US-FR-007: Book catalog lookup

**As** an authenticated user,

**I want** to browse the book catalog,

**So that** I can find out which books are available in the library.

**Endpoint:** `GET /api/v1/books`

**Cache Strategy:** Create/Get `cache:books:catalog:{filters_hash}`

**Acceptance criteria:**

- [ ]  The system must return the list of registered books.
- [ ]  It must be possible to filter by `title`, `author`, and `isbn`.
- [ ]  It must be possible to filter for available books only.
- [ ]  It must be possible to sort results by `title` and `published_year`.
- [ ]  The system must allow sorting results in ascending and descending order.
- [ ]  The system must allow paginating results.
- [ ]  The system must first query the cache before accessing the database.
- [ ]  If the data is found in the cache (`Cache Hit`), the system must respond using the stored data.
- [ ]  If the data is not found in the cache (`Cache Miss`), the system must query the database, store the result in the cache, and respond with that information.
- [ ]  The system must log successful and failed executions of the process.
- [ ]  The endpoint returns a paginated collection of the book catalog: `id`, `title`, `isbn`, `author`, `published_year`, `total_copies`, `available_copies`, `created_at`, `updated_at`.
- [ ]  Returns status `200 OK` if the query was performed successfully.
- [ ]  Returns status `401 Unauthorized` if the token is invalid or missing.
- [ ]  Returns status `500 Internal Server Error` if an unexpected error occurs.

### Module 3: Loan management

### US-FR-008: Registering a loan

**As** a `MEMBER`,

**I want** to register the loan of a book,

**So that** I can borrow it.

**Endpoint:** `POST /api/v1/loans`

**Cache Strategy:** Invalidate `cache:books:catalog:{filters_hash}`, Invalidate `cache:loans:catalog:{filters_hash}`, Invalidate `cache:loans:member:{member_id}:{filters_hash}`

**Acceptance criteria:**

- [ ]  Only a user with the `MEMBER` role can register loans.
- [ ]  The `MEMBER` must provide the book's identifier (`book_id`).
- [ ]  The system must verify that the book exists.
- [ ]  The system must verify that the book has available copies.
- [ ]  The system must not allow a `MEMBER` to register a loan for the same book more than once while they have an active loan for it.
- [ ]  A `MEMBER` cannot exceed the maximum number of allowed active loans.
- [ ]  When registering the loan, the system must decrease the book's `available_copies` by one.
- [ ]  The loan must be registered with the `ACTIVE` status.
- [ ]  The system must invalidate the book catalog cache after registering the loan.
- [ ]  The system must log successful and failed executions of the process.
- [ ]  The endpoint returns the created loan's data: `id`, `member_id`, `book_id`, `status`, `loaned_at`, `returned_at`.
- [ ]  Returns status `201 Created` if the loan was registered successfully.
- [ ]  Returns status `400 Bad Request` if any field fails format validation.
- [ ]  Returns status `401 Unauthorized` if the token is invalid or missing.
- [ ]  Returns status `403 Forbidden` if the authenticated user does not have the `MEMBER` role.
- [ ]  Returns status `404 Not Found` if the book does not exist.
- [ ]  Returns status `409 Conflict` if the loan cannot be made due to a business rule.
- [ ]  Returns status `422 Unprocessable Entity` if a required field is missing or malformed.
- [ ]  Returns status `500 Internal Server Error` if an unexpected error occurs.

### US-FR-009: Registering a return

**As** a `MEMBER`,

**I want** to register the return of one of my loans,

**So that** I can return the book to the library.

**Endpoint:** `PATCH /api/v1/loans/{loan_id}/return`

**Cache Strategy:** Invalidate `cache:books:catalog:{filters_hash}`, Invalidate `cache:loans:catalog:{filters_hash}`, Invalidate `cache:loans:member:{member_id}:{filters_hash}`

**Acceptance criteria:**

- [ ]  Only a user with the `MEMBER` role can register returns.
- [ ]  The `MEMBER` must provide the loan's identifier (`loan_id`).
- [ ]  The system must verify that the loan exists.
- [ ]  The system must verify that the loan belongs to the authenticated user.
- [ ]  The system must verify that the loan is in the `ACTIVE` status.
- [ ]  When registering the return, the system must increase the book's `available_copies` by one.
- [ ]  The loan must be updated to the `RETURNED` status.
- [ ]  The return date and time must be recorded automatically.
- [ ]  The system must invalidate the book catalog cache after registering the return.
- [ ]  The system must log successful and failed executions of the process.
- [ ]  The endpoint returns the updated loan's data: `id`, `member_id`, `book_id`, `status`, `loaned_at`, `returned_at`.
- [ ]  Returns status `200 OK` if the return was registered successfully.
- [ ]  Returns status `401 Unauthorized` if the token is invalid or missing.
- [ ]  Returns status `403 Forbidden` if the authenticated user does not have the `MEMBER` role.
- [ ]  Returns status `404 Not Found` if the loan does not exist.
- [ ]  Returns status `409 Conflict` if the loan has already been returned.
- [ ]  Returns status `500 Internal Server Error` if an unexpected error occurs.

### US-FR-010: Viewing my loans

**As** a `MEMBER`,

**I want** to view my loans,

**So that** I can know the status of the books I have borrowed.

**Endpoint:** `GET /api/v1/loans/me`

**Cache Strategy:** Create/Get `cache:loans:member:{member_id}:{filters_hash}`

**Acceptance criteria:**

- [ ]  Only a user with the `MEMBER` role can view their loans.
- [ ]  The system must return only the loans belonging to the authenticated user.
- [ ]  It must be possible to filter by `status`.
- [ ]  It must be possible to sort by `loaned_at` and `returned_at`.
- [ ]  The system must allow sorting results in ascending and descending order.
- [ ]  The system must allow paginating results.
- [ ]  The system must first query the cache before accessing the database.
- [ ]  If the data is found in the cache (Cache Hit), the system must respond using the stored data.
- [ ]  If the data is not found in the cache (Cache Miss), the system must query the database, store the result in the cache, and respond with that information.
- [ ]  The system must log successful and failed executions of the process.
- [ ]  The endpoint returns a paginated collection of loans: `id`, `member_id`, `book_id`, `status`, `loaned_at`, `returned_at`.
- [ ]  Returns status `200 OK` if the query was performed successfully.
- [ ]  Returns status `401 Unauthorized` if the token is invalid or missing.
- [ ]  Returns status `403 Forbidden` if the authenticated user does not have the `MEMBER` role.
- [ ]  Returns status `500 Internal Server Error` if an unexpected error occurs.

### US-FR-011: Viewing loans for all users

**As** a `LIBRARIAN`,

**I want** to view the registered loans,

**So that** I can oversee the status of the library's loans.

**Endpoint:** `GET /api/v1/loans`

**Cache Strategy:** Create/Get `cache:loans:catalog:{filters_hash}`

**Acceptance criteria:**

- [ ]  Only a user with the `LIBRARIAN` role can view the loans.
- [ ]  The system must return the registered loans of all users.
- [ ]  It must be possible to filter by `member_id`, `book_id`, and `status`.
- [ ]  It must be possible to sort by `loaned_at` and `returned_at`.
- [ ]  The system must allow sorting results in ascending and descending order.
- [ ]  The system must allow paginating results.
- [ ]  The system must first query the cache before accessing the database.
- [ ]  If the data is found in the cache (Cache Hit), the system must respond using the stored data.
- [ ]  If the data is not found in the cache (Cache Miss), the system must query the database, store the result in the cache, and respond with that information.
- [ ]  The system must log successful and failed executions of the process.
- [ ]  The endpoint returns a paginated collection of loans: `id`, `member_id`, `book_id`, `status`, `loaned_at`, `returned_at`.
- [ ]  Returns status `200 OK` if the query was performed successfully.
- [ ]  Returns status `401 Unauthorized` if the token is invalid or missing.
- [ ]  Returns status `403 Forbidden` if the authenticated user does not have the `LIBRARIAN` role.
- [ ]  Returns status `500 Internal Server Error` if an unexpected error occurs.

---

## 4. Data Models

[SQL Data Model](https://dbdiagram.io/d/Verbose-Potato-6a51543c4ac62e474c7ccd79)

### `Users` Model — DB: PostgreSQL

| Field | Type | Constraints | Description |
| --- | --- | --- | --- |
| id | UUID | PK | Unique identifier of the user. |
| name | VARCHAR(100) | NOT NULL | Full name of the user. |
| email | VARCHAR(255) | NOT NULL · UNIQUE · Indexed | User's email address. |
| password | VARCHAR(255) | NOT NULL | Password hashed using Argon2. |
| role | ENUM(`LIBRARIAN`, `MEMBER`) | NOT NULL | User's role within the system. |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | Record creation date. |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | Date of the last update. |

### `Books` Model — DB: PostgreSQL

| Field | Type | Constraints | Description |
| --- | --- | --- | --- |
| id | UUID | PK | Unique identifier of the book. |
| title | VARCHAR(255) | NOT NULL · Indexed | Title of the book. |
| isbn | VARCHAR(20) | NOT NULL · UNIQUE · Indexed | ISBN code of the book. |
| author | VARCHAR(100) | NOT NULL · Indexed | Author of the book. |
| published_year | SMALLINT | NOT NULL · Indexed | Year of publication. |
| total_copies | INTEGER | NOT NULL | Total number of registered copies. |
| available_copies | INTEGER | NOT NULL | Number of copies currently available. |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | Record creation date. |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | Date of the last update. |

### `Loans` Model — DB: PostgreSQL

| Field | Type | Constraints | Description |
| --- | --- | --- | --- |
| id | UUID | PK | Unique identifier of the loan. |
| member_id | UUID | FK → Users.id · Indexed | User who made the loan. |
| book_id | UUID | FK → Books.id · Indexed | Borrowed book. |
| status | ENUM(`ACTIVE`, `RETURNED`) | NOT NULL · Indexed | Current status of the loan. |
| loaned_at | TIMESTAMP WITH TIME ZONE | NOT NULL · Indexed | Date and time the loan was made. |
| returned_at | TIMESTAMP WITH TIME ZONE | NULL · Indexed | Date and time of the return. |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | Record creation date. |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | Date of the last update. |

### Cache Keys — DB: Redis

| Key | TTL | Value | Description |
| --- | --- | --- | --- |
| `cache:books:catalog:{filters_hash}` | 10 min | Serialized list of books | Book catalog according to filters, sorting, and pagination. |
| `cache:loans:catalog:{filters_hash}` | 10 min | Serialized list of loans | Global loan query for `LIBRARIAN`. |
| `cache:loans:member:{member_id}:{filters_hash}` | 10 min | Serialized list of loans | Loan query for a `MEMBER`. |
