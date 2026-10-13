# JamesDoe V6 --- Learning Roadmap

## Purpose

This roadmap tracks the practical lessons for building the JamesDoe V6
backend while learning the Python ecosystem through direct comparison
with familiar PHP/Laravel concepts.

The approach is:

-   learn by building the real application;
-   introduce new concepts when the application needs them;
-   map unfamiliar Python/FastAPI/SQLAlchemy concepts to PHP/Laravel
    where useful;
-   avoid adding infrastructure or abstractions before there is a
    concrete requirement;
-   move quickly through repetitive implementation once a pattern is
    understood.

------------------------------------------------------------------------

# Phase 1 --- Python, FastAPI, Database & Migration Foundations

## Lessons 1--4 --- Python, FastAPI, Configuration & Database Infrastructure

### Topics covered

-   Python modules and packages
-   Python type annotations
-   functions, `self`, `@property`, and f-strings
-   Pydantic Settings and `.env`
-   FastAPI application structure
-   synchronous vs asynchronous execution
-   SQLAlchemy Engine
-   connection pooling
-   SQLAlchemy Session
-   Session factory
-   request-scoped Sessions
-   FastAPI dependency injection
-   `yield`, generators, `try/finally`
-   Psycopg 3
-   PostgreSQL connectivity
-   application health vs database health

## Lessons 5--6 --- Alembic and Database Migrations

### Topics covered

-   Alembic initialization and configuration
-   online and offline migrations
-   revisions and `down_revision`
-   revision chains
-   `upgrade()` and `downgrade()`
-   Alembic `op`
-   SQLAlchemy migration types
-   identity columns
-   nullability and server defaults
-   `TIMESTAMPTZ`
-   unique and check constraints
-   indexes
-   database comments
-   application-controlled enums
-   migration SQL inspection
-   `alembic current`
-   `alembic history`
-   `alembic_version` vs Laravel's `migrations` table
-   application-enforced referential integrity
-   no database-level foreign keys or cascading deletes
-   monetary values stored as exact strings

The 11 core-domain migrations are complete.

This phase represents the lessons already completed. It remains part of
the roadmap so that, months later, the full learning sequence is visible
from the beginning rather than starting only from the current position.

------------------------------------------------------------------------

# Phase 2 --- SQLAlchemy ORM

## Lesson 7 --- First ORM Model

Build the `Collection` model.

Topics:

-   what an ORM model represents;
-   Eloquent Model vs SQLAlchemy model;
-   `DeclarativeBase`;
-   `Mapped[...]`;
-   `mapped_column()`;
-   `__tablename__`;
-   mapping an existing PostgreSQL table without changing it;
-   separating ORM models from Alembic migrations.

Goal:

``` text
collections PostgreSQL table
        ↕
SQLAlchemy Collection model
```

## Lesson 8 --- Remaining Core Models

Implement:

-   Artwork
-   Image
-   Publication
-   PublicationGroup
-   Product
-   ProductVariant

Introduce new Python/SQLAlchemy concepts only when they naturally
appear:

-   `str | None`;
-   `datetime`;
-   `date`;
-   UUID values;
-   nullable fields;
-   Python-side vs database-side defaults;
-   application enum/string fields.

Move quickly through repeated column-mapping patterns.

## Lesson 9 --- Relationships Without Database Foreign Keys

Implement the domain relationships:

``` text
Collection ↔ Artwork
Artwork ↔ Image
Publication ↔ Image
PublicationGroup ↔ Publication
Product → ProductVariant
```

Topics:

-   `relationship()`;
-   `back_populates`;
-   one-to-many;
-   many-to-many;
-   association models;
-   explicit join conditions;
-   how SQLAlchemy relationships normally use foreign-key metadata;
-   configuring relationships when PostgreSQL deliberately has no FK
    constraints;
-   keeping referential-integrity and delete behaviour in the
    application.

## Lesson 10 --- Querying with SQLAlchemy

Topics:

-   `session.get()`;
-   `select()`;
-   `where()`;
-   `session.execute()`;
-   `scalars()`;
-   `scalar_one()`;
-   `scalar_one_or_none()`;
-   ordering;
-   simple filtering.

Laravel comparisons:

``` text
Model::find()
Model::where()
->first()
->get()
```

## Lesson 11 --- Writing Data and Unit of Work

Topics:

-   constructing ORM objects;
-   `session.add()`;
-   `flush()`;
-   `commit()`;
-   `rollback()`;
-   `refresh()`;
-   transaction boundaries;
-   SQLAlchemy identity map;
-   SQLAlchemy Unit of Work.

Compare the SQLAlchemy lifecycle with Eloquent's familiar:

``` php
$model->save();
```

## Lesson 12 --- Relationship Loading and N+1

Topics:

-   navigating ORM relationships;
-   lazy loading;
-   eager loading;
-   `selectinload()`;
-   `joinedload()`;
-   N+1 queries;
-   choosing loading strategies deliberately.

------------------------------------------------------------------------

# Phase 3 --- Pydantic and the FastAPI Layer

## Lesson 13 --- Pydantic API Models

Understand why:

``` text
ORM model ≠ API response model
```

Topics:

-   Pydantic `BaseModel`;
-   request models;
-   response models;
-   `model_config`;
-   `from_attributes`;
-   nested models;
-   validation;
-   serialization;
-   controlling the public API representation independently of
    persistence.

## Lesson 14 --- First Real API Endpoints

Build initial read endpoints such as:

``` text
GET /collections
GET /collections/{slug}
```

Follow the complete request path:

``` text
HTTP
 ↓
FastAPI
 ↓
Depends(get_db)
 ↓
SQLAlchemy Session
 ↓
ORM query
 ↓
Pydantic response
 ↓
JSON
```

## Lesson 15 --- API Structure and Behaviour

Topics:

-   routers;
-   endpoint organization;
-   dependency organization;
-   HTTP status codes;
-   application exceptions;
-   API error responses;
-   pagination;
-   filtering;
-   ordering;
-   not-found behaviour;
-   keeping HTTP concerns separate from persistence concerns.

------------------------------------------------------------------------

# Phase 4 --- Authentication and API Protection

## Lesson 16 --- Authentication Architecture

Establish where authentication belongs in the application.

Topics:

-   authentication vs authorization;
-   identities/principals;
-   authentication dependencies;
-   protecting endpoints;
-   public vs authenticated API routes;
-   `401 Unauthorized` vs `403 Forbidden`;
-   where authentication should and should not interact with
    ORM/application code.

## Lesson 17 --- OAuth 2.0 in FastAPI

Implementation-focused rather than reteaching OAuth fundamentals.

Topics:

-   how FastAPI represents OAuth security dependencies;
-   `Authorization` headers;
-   Bearer tokens;
-   `OAuth2PasswordBearer` where appropriate;
-   `Security`;
-   resolving the current authenticated principal;
-   protecting routes;
-   scopes and permissions where useful;
-   OAuth 2.0 vs authentication;
-   OpenID Connect where identity/login requirements make it relevant.

The exact OAuth flow/provider should be chosen from the application's
real authentication requirements rather than assumed in advance.

## Lesson 18 --- API Rate Limiting

Topics:

-   why concurrency and rate limiting are different;
-   per-IP limits;
-   per-user/token limits;
-   global limits;
-   `429 Too Many Requests`;
-   `Retry-After`;
-   fixed-window concepts;
-   sliding-window concepts;
-   token-bucket concepts;
-   choosing a strategy appropriate to the API.

Start with the simplest implementation justified by the application.

Then understand why multiple application instances require shared state:

``` text
App instance 1 ─┐
App instance 2 ─┼→ shared rate-limit state
App instance 3 ─┘
```

This can provide a concrete reason to introduce Redis later rather than
adding Redis pre-emptively.

------------------------------------------------------------------------

# Phase 5 --- Building the Real JamesDoe API

After the foundations above, development becomes increasingly
feature-driven rather than following a rigid lesson sequence.

Topics will be introduced when the application needs them.

Likely areas include:

-   collection endpoints;
-   artwork endpoints;
-   publication endpoints;
-   product and variant endpoints;
-   image handling;
-   visibility rules;
-   soft deletion;
-   application-enforced referential integrity;
-   transaction boundaries;
-   repositories where they provide real value;
-   services where business logic requires them;
-   validation rules;
-   API tests;
-   database integration tests;
-   authentication/authorization integration;
-   rate-limit integration;
-   logging and observability;
-   production configuration.

The guiding rule remains:

> Introduce an abstraction, dependency, or infrastructure component when
> a concrete application requirement justifies it.

------------------------------------------------------------------------

# Current Position

``` text
Python / FastAPI foundations             ✓
SQLAlchemy Engine + Session              ✓
PostgreSQL                               ✓
Alembic                                 ✓
11 core migrations                       ✓
core PostgreSQL schema                   ✓

NEXT
 ↓
Lesson 7 — First SQLAlchemy ORM Model
 ↓
Collection
```

## Overall Path

``` text
PostgreSQL schema
        ✓
Alembic migrations
        ✓
        ↓
SQLAlchemy ORM models
        ↓
SQLAlchemy relationships
        ↓
SQLAlchemy querying/writes
        ↓
Pydantic models
        ↓
FastAPI endpoints
        ↓
API structure
        ↓
Authentication / OAuth 2.0
        ↓
Rate limiting
        ↓
Feature-driven JamesDoe API development
```

This roadmap is intentionally not fixed forever. Later lessons can be
reordered when implementation experience exposes a better learning
sequence or a real JamesDoe requirement makes a topic immediately
relevant.
