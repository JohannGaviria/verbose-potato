# Architecture - Verbose Potato

> Defines the architectural organization of the system, the dependency flow between its layers, and the design decisions that keep business logic independent from external technologies.

# Table of Contents

1. [Overview](#1-overview)
2. [General Structure](#2-general-structure)
3. [Architectural Layers](#3-architectural-layers)
4. [Request Flow](#4-request-flow)
5. [Architectural Decisions](#5-architectural-decisions)
6. [Project Structure](#6-project-structure)

---

# 1. Overview

**Verbose Potato** is built following **Hexagonal Architecture (Ports & Adapters)** and organized as a **domain-oriented Modular Monolith**.

The main goal of the architecture is to keep business rules completely independent from external frameworks and technologies such as FastAPI, PostgreSQL, Redis, or SQLAlchemy.

The application is divided into independent functional modules, where each module encapsulates its own use cases, business rules, ports, and adapters. This organization promotes high cohesion, low coupling, and makes the system easier to maintain and test.

---

# 2. General Structure

```
src/
├── modules/
│   ├── auth/
│   ├── books/
│   └── loans/
│
├── shared/
│
└── main.py
```

## Principles

- High cohesion within each module.
- Low coupling between modules.
- Dependencies always point toward the domain.
- Business logic is independent of frameworks.
- Infrastructure implements the contracts defined by the domain.

---

# 3. Architectural Layers

All modules follow the same internal organization.

```
application/
domain/
infrastructure/
presentation/
```

| Layer | Responsibility |
| --- | --- |
| **Presentation** | Exposes the HTTP API, validates requests, transforms responses, and configures dependency injection. |
| **Application** | Contains the Use Cases and DTOs. Coordinates the execution of system operations. |
| **Domain** | Contains the Entities, Value Objects, Exceptions, and Ports. This is where all business logic resides. |
| **Infrastructure** | Implements persistence, the caching system, authentication, and any external service used by the application. |

## Dependency Flow

```
Presentation
      │
Application
      │
   Domain
      ▲
Infrastructure
```

The domain never depends on any other layer.

---

# 4. Request Flow

All requests follow the same execution flow.

```
HTTP Request
      │
FastAPI Route
      │
Request Schema
      │
Use Case
      │
Repository Port
      │
Repository Adapter
      │
PostgreSQL / Redis
      │
HTTP Response
```

1. The HTTP request arrives at a FastAPI endpoint.
2. The presentation layer validates the received data using schemas.
3. The validated data is transformed into an application DTO.
4. The Use Case coordinates the requested operation.
5. The domain executes the business rules.
6. The infrastructure implements the ports defined by the domain to access the database, cache, or other external services.
7. The result is transformed into an HTTP response for the client.

---

# 5. Architectural Decisions

The project adopts the following architectural decisions:

- Hexagonal Architecture (Ports & Adapters).
- Domain-oriented Modular Monolith.
- One module per business capability.
- Use Cases as the entry point to application logic.
- Value Objects to encapsulate and validate domain rules.
- Repository pattern to abstract persistence.
- PostgreSQL as the primary database.
- Redis for caching.
- JWT for authentication.
- Argon2 for secure password storage.
- Structlog for structured event logging.

---

# 6. Project Structure

```
src/
├── modules/
│
│   ├── auth/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   └── presentation/
│   │
│   ├── books/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   └── presentation/
│   │
│   └── loans/
│       ├── application/
│       ├── domain/
│       ├── infrastructure/
│       └── presentation/
│
├── shared/
│
└── tests/
```

All modules follow the same internal structure to maintain consistency across the project, ease maintenance, and simplify the addition of new features.
