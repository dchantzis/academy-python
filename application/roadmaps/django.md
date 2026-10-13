# JamesDoe V6 --- Complementary Django Learning Roadmap

## Purpose

Follow this roadmap **after the FastAPI / SQLAlchemy JamesDoe V6 backend
is sufficiently complete to act as our reference implementation**.

We are not redesigning JamesDoe or relearning Python. We are rebuilding
the same system with Django so we can compare:

``` text
Laravel
   ↕
FastAPI / SQLAlchemy
   ↕
Django
```

The goals are to learn Django through an already-understood domain, see
which pieces Django integrates for us, and understand Django conventions
rather than mechanically reproducing the FastAPI architecture.

# Phase 1 --- Django Foundations

## Lesson 1 --- Django Project Anatomy

-   Django project vs Django app
-   `manage.py`
-   settings and environment configuration
-   URL configuration
-   PostgreSQL connection
-   development server
-   where Django conventions replace pieces assembled manually in
    FastAPI

## Lesson 2 --- Django Models and ORM

Recreate the JamesDoe core domain models.

-   `models.Model`
-   fields, UUIDs and timestamps
-   nullability and defaults
-   indexes and uniqueness
-   check constraints
-   model metadata
-   application enum choices
-   implications of our deliberate no-database-FK convention

Compare Django models with SQLAlchemy declarative models and Eloquent
models.

## Lesson 3 --- Django Migrations

-   `makemigrations`
-   `migrate`
-   migration dependencies
-   schema operations
-   data migrations
-   generated SQL
-   rollback behaviour
-   migration history

Compare Django migrations with Alembic and Laravel migrations.

# Phase 2 --- Querying, Relationships and Data

## Lesson 4 --- Django QuerySets

-   `objects`
-   `get()`
-   `filter()`
-   `exclude()`
-   `first()`
-   ordering
-   existence checks
-   QuerySet laziness
-   one vs many results

Compare equivalent Eloquent, SQLAlchemy and Django ORM queries.

## Lesson 5 --- Creating and Updating Data

-   model construction
-   `save()`
-   `create()`
-   updates and deletes
-   transactions
-   atomic operations
-   validation boundaries
-   application-level integrity

Compare Django's model API with SQLAlchemy's Session / Unit of Work.

## Lesson 6 --- Relationships and Loading

Recreate:

-   Collection ↔ Artwork
-   Artwork ↔ Image
-   Publication ↔ Image
-   PublicationGroup ↔ Publication
-   Product → ProductVariant

Cover reverse relationships, many-to-many relationships,
through/association models, our no-database-FK requirements,
`select_related()`, `prefetch_related()`, and N+1 queries.

# Phase 3 --- Django REST Framework

Use Django REST Framework so the API can be compared directly with
FastAPI.

## Lesson 7 --- Serializers

-   serializers
-   `ModelSerializer`
-   validation
-   serialization/deserialization
-   nested representations
-   ORM model vs public API representation

Compare DRF serializers with Pydantic models.

## Lesson 8 --- First API Endpoints

Recreate representative endpoints:

``` text
GET /collections
GET /collections/{slug}
GET /artworks
GET /artworks/{slug}
GET /publications
GET /publications/{slug}
GET /products
```

Compare:

``` text
FastAPI:
route → dependency → SQLAlchemy → Pydantic → JSON

Django / DRF:
URL → view → Django ORM → serializer → JSON
```

## Lesson 9 --- API Structure and Behaviour

-   views, generic views and viewsets
-   routers
-   HTTP status codes
-   not-found behaviour
-   validation errors
-   exception handling
-   pagination
-   filtering
-   ordering

# Phase 4 --- Django's Integrated Features

## Lesson 10 --- Django Admin

-   model registration
-   lists, search and filters
-   editing
-   relationship editing
-   admin customization
-   evaluate whether Django Admin could act as a practical JamesDoe CMS

## Lesson 11 --- Management Commands

Create useful terminal commands.

-   custom management commands
-   arguments/options
-   ORM access
-   imports
-   maintenance operations
-   development-data commands

Compare:

``` text
Laravel Artisan
      ↕
Django management commands
      ↕
FastAPI-side CLI
```

Do not create CRUD commands merely for completeness.

## Lesson 12 --- Seed and Development Data

-   fixtures
-   management-command seeders
-   factories/test data where useful
-   repeatable local datasets
-   importing real JamesDoe content

# Phase 5 --- Authentication and API Protection

## Lesson 13 --- Django Authentication

-   Django users/authentication
-   sessions
-   permissions
-   groups
-   authentication middleware
-   request users
-   protecting views

Compare Django's integrated approach with our explicit FastAPI
authentication architecture.

## Lesson 14 --- API Authentication / OAuth

Using the same requirements chosen for FastAPI:

-   Bearer/API authentication
-   OAuth 2.0 integration where required
-   OpenID Connect where relevant
-   authenticated principals
-   permissions/scopes
-   `401` vs `403`

## Lesson 15 --- API Rate Limiting

-   DRF throttling
-   anonymous/IP limits
-   per-user limits
-   custom throttles
-   shared state
-   caching
-   Redis when justified
-   `429 Too Many Requests`

Compare directly with the FastAPI implementation.

# Phase 6 --- Request Tracing and Audit

## Lesson 16 --- `ip_trace`

Design and implement the standard JamesDoe requirement:

> Every HTTP request is traced.

We will decide the actual schema later.

Topics will include request metadata, IP handling, request IDs,
timestamps, middleware, exclusions if any, retention, and
privacy/security considerations.

## Lesson 17 --- `api_audit_log`

Design and implement:

> Every API request and response is tracked.

We will decide the actual schema later.

Topics will include method/path, request and response payload handling,
status, authenticated identity, duration, correlation with `ip_trace`,
sensitive-field redaction, exceptions, storage, and retention.

# Phase 7 --- Testing and Production

## Lesson 18 --- Testing

-   Django test infrastructure
-   pytest integration where useful
-   database tests
-   API tests
-   authentication tests
-   relationship tests
-   management-command tests
-   tracing/audit tests

Where practical, reuse the behavioural expectations established by the
FastAPI implementation.

## Lesson 19 --- Production Deployment

-   production settings
-   secrets/environment variables
-   application server
-   reverse proxy
-   database configuration
-   deployment migrations
-   logging
-   restart behaviour
-   Docker
-   deployment on Theseus / DigitalOcean
-   comparison with FastAPI deployment

# Final Comparison --- FastAPI vs Django vs Laravel

Compare:

-   project structure
-   framework philosophy
-   ORM design
-   migrations
-   relationships
-   query syntax
-   transactions
-   API validation
-   routing
-   dependency handling
-   authentication
-   middleware
-   CLI/management commands
-   admin/CMS capabilities
-   testing
-   deployment
-   explicit vs framework-provided behaviour

The objective is not to declare one framework universally better. It is
to understand what Django provides, what FastAPI leaves explicit, and
which trade-offs matter for a particular application.

# Expected Starting Point

Before starting:

``` text
JamesDoe requirements       KNOWN
PostgreSQL/domain design    KNOWN
Python fundamentals         KNOWN
API behaviour               KNOWN
FastAPI implementation      KNOWN

                ↓

          Learn Django
       through comparison
```

This should make the Django journey substantially faster than the
original FastAPI roadmap.

# Overall Path

``` text
Phase 1  Django foundations
        ↓
Phase 2  ORM queries + relationships
        ↓
Phase 3  Django REST Framework
        ↓
Phase 4  Admin + management commands + data
        ↓
Phase 5  Authentication + rate limiting
        ↓
Phase 6  ip_trace + api_audit_log
        ↓
Phase 7  Testing + deployment
        ↓
FastAPI ↔ Django ↔ Laravel comparison
```
