# JamesDoe V6 --- Learning and Architecture Handoff

## Purpose

This is the cross-stack handoff for the JamesDoe V6 learning programme.
It preserves the overall roadmap, teaching approach, and architecture
discussions so a new chat can continue without reconstructing this
conversation.

Detailed Python/FastAPI/SQLAlchemy lesson material belongs in
`jamesdoe-v6-python-backend-foundations.md`. This document records the
wider map and decisions rather than duplicating those lessons.

## Current Learning Position

The active track is the Python/FastAPI backend.

``` text
Phase 1 — Python / FastAPI / Database Foundations       COMPLETE

Phase 2 — SQLAlchemy ORM
Lesson 7  — First SQLAlchemy ORM Model                  COMPLETE
Lesson 8  — Remaining Core Models                       COMPLETE
Lesson 9  — Relationships Without Database FKs          COMPLETE
Lesson 10 — Querying with SQLAlchemy                    COMPLETE
Lesson 11 — Writing Data and Unit of Work               COMPLETE
Lesson 12 — Relationship Loading and N+1                NEXT
```

The immediate next lesson is **Lesson 12 --- Relationship Loading and
the N+1 Problem**.

Do not restart the SQLAlchemy material from the beginning unless
requested. The detailed canonical backend lesson record is in
`jamesdoe-v6-python-backend-foundations.md`.

## Teaching Approach

The learner is an experienced PHP/Laravel engineer with roughly two
decades of engineering experience. General engineering concepts are
familiar; Python syntax, conventions, ecosystem and the newer frontend
stack are the learning areas.

Teaching should:

-   work one concept at a time and remain interactive;
-   use small practical experiments and repetition;
-   map unfamiliar concepts to PHP/Laravel where useful;
-   explicitly distinguish Python, FastAPI, SQLAlchemy, Alembic,
    Pydantic and Psycopg;
-   avoid treating the learner as a programming beginner;
-   move faster after a pattern has already been demonstrated;
-   avoid premature abstractions;
-   preserve sound existing project conventions;
-   treat explicitly LOCKED decisions as canonical unless a concrete
    requirement forces reconsideration.

## Current Python / FastAPI Roadmap

``` text
Python / FastAPI / DB foundations
        ✓
SQLAlchemy models
        ✓
SQLAlchemy relationships
        ✓
SQLAlchemy querying
        ✓
SQLAlchemy writes / Unit of Work
        ✓
Relationship loading / N+1
        NEXT
        ↓
Pydantic request / response models
        ↓
FastAPI API design and endpoints
        ↓
Authentication / API protection
        ↓
Real JamesDoe domain API
        ↓
Seed / development-data tooling as useful
```

The Python backend should be completed rather than abandoned when
frontend learning begins.

## Planned TypeScript Crash Course

A short, focused TypeScript crash course is planned after the current
Python/SQLAlchemy work reaches a sensible stopping point.

This is not programming or JavaScript from zero. The learner already has
substantial JavaScript experience, especially classic browser JavaScript
and jQuery-style development.

Target discussed: roughly **4--6 focused hours**.

Topics:

``` text
modern JavaScript essentials needed for TypeScript
types and inference
interfaces and type aliases
objects
arrays and tuples
functions
optional and nullable values
unions and literal types
type narrowing
generics
classes and access modifiers
enums versus unions
utility types
modules
async / await
Promise<T>
typing API JSON
small practical TypeScript exercise/application
```

Use PHP 8.x ↔ TypeScript comparisons where useful. The goal is enough
fluency to move confidently into React, not exhaustive TypeScript
mastery first.

## React.js Direction

React is the next major frontend technology.

The important conceptual transition is:

``` text
Traditional jQuery / MooTools style

rendered HTML
    ↓
find DOM elements
    ↓
attach event handlers
    ↓
manually mutate DOM
```

versus:

``` text
React

application state / data
    ↓
components describe UI
    ↓
React updates rendered DOM
```

React is fundamentally the UI/component layer. Initially it should be
understood as the frontend consuming the JamesDoe FastAPI JSON API.

Learn the fundamentals and apply them rather than completing a large
generic React course first.

## Next.js Direction

After React fundamentals, the current direction is **Next.js
fundamentals**, followed by the JamesDoe website.

``` text
TypeScript crash course
        ↓
React fundamentals
        ↓
Next.js fundamentals
        ↓
JamesDoe website implementation
```

This became important after clarifying the boundary between the JamesDoe
domain API and the jamesdoe.com website/presentation application.

## Role of Node.js

Using TypeScript, React or Next.js does **not** mean the existing
FastAPI backend should be replaced with Node.js.

Initially Node.js mainly provides the runtime/tooling ecosystem around
the frontend:

``` text
Node.js
npm
TypeScript tooling
React tooling
Next.js
build/dev tooling
```

The JamesDoe domain backend remains Python/FastAPI.

A separate Node.js backend/service may later be useful as a learning
exercise or complementary system, but it is not currently a locked part
of the production architecture.

Do not introduce a second API merely to gain Node.js experience.

## Critical Architecture Distinction: Domain API vs Website

A key clarification was that FastAPI should **not define the structure
of jamesdoe.com**.

The FastAPI application is the **JamesDoe domain API** and owns concepts
such as:

``` text
artworks
collections
images
publications
publication groups
products
product variants
```

Website/presentation concepts are separate:

``` text
/
/about
/contact
/art
/art/[slug]
/coffee-and-sketch
/prints

layouts
navigation
page composition
presentation
website copy
```

Current direction:

``` text
jamesdoe.com
Next.js + React + TypeScript
        │
        │ HTTP / JSON
        ▼
JamesDoe Domain API
Python + FastAPI
        │
        ▼
SQLAlchemy
        │
        ▼
PostgreSQL
```

For example, `/art/motorcycles` can be a Next.js website route while the
website obtains domain data through an API operation conceptually like
`GET /collections/motorcycles`.

FastAPI knows the collection. It does not need to know which public
website route displays it.

## Website Structure and Presentation

Initially Next.js can own:

``` text
routes
layouts
navigation
page composition
presentation
static website copy
```

These concerns do not automatically require another database.

**Do not create a second database simply because Next.js is
introduced.**

Start with website structure represented naturally in the Next.js
application and consume domain data from FastAPI.

## Possible Future Website / CMS Datastore

A separate website/CMS datastore may become justified if genuine
requirements emerge for dynamically managed concepts such as:

``` text
dynamic pages
navigation management
landing-page composition
content blocks
SEO metadata
redirects
site settings
presentation configuration
```

A possible future shape is:

``` text
                 jamesdoe.com
          Next.js / React / TypeScript
                    │
           ┌────────┴────────┐
           │                 │
           ▼                 ▼
     Domain API         Website / CMS data
      FastAPI           separate concern
           │
           ▼
    Domain PostgreSQL
```

A second website/CMS database is **not currently locked**. Do not design
it until concrete requirements justify it.

This is consistent with the earlier decision not to force website
presentation concepts such as `presentation_settings` into the core
domain schema.

## Complementary System / Second Backend Discussion

Another discussion concerned what to build after gaining confidence with
FastAPI.

A second system using **TypeScript/Node.js** could broaden backend
experience in addition to Python/FastAPI. The important principle is
that it should **complement the FastAPI domain API rather than
arbitrarily duplicate it**.

No specific complementary Node.js system has been selected or locked.

NestJS has been mentioned as one possible Node/TypeScript backend
framework, but it is **not a locked choice**.

## Current JamesDoe Domain Architecture

``` text
FastAPI
    ↓
Python application/domain logic
    ↓
SQLAlchemy 2.x
    ↓
Psycopg 3
    ↓
PostgreSQL 17
```

Current backend decisions include:

``` text
SQLAlchemy 2.x synchronous
Psycopg 3 synchronous
PostgreSQL 17
Alembic
one SQLAlchemy Session per HTTP request
FastAPI dependency manages Session lifetime
application/service operation owns explicit commit/rollback
explicit migrations
no automatic migrations at application startup
database infrastructure under app/database/
configuration under app/config.py
```

Detailed reasoning belongs in the Python foundations document.

## Core Domain Direction

The core schema includes:

``` text
collections
artworks
collection_artwork
images
artwork_image
publications
publication_image
publication_groups
publication_group_publication
products
product_variants
```

Important design choices include:

-   no database-level foreign-key constraints;
-   no database-level cascade deletes;
-   relationships/integrity handled intentionally in application logic;
-   ORM relationships use explicit joins;
-   products are polymorphic across domain sellables such as
    artwork/publication;
-   product variants represent concrete purchasable options;
-   website/presentation concepts are not part of the core domain merely
    because the public website needs pages.

## Additional Backend Requirements to Revisit

Two operational capabilities are wanted later:

### `ip_trace`

Trace every HTTP request.

### `api_audit_log`

Track API requests and responses.

These should not derail the current ORM lessons. Revisit them when the
course reaches FastAPI middleware/request lifecycle and the real API.

Design considerations include:

``` text
correlation/request IDs
request metadata
response metadata
privacy
redaction
sensitive payloads
retention
storage cost
security
failure behaviour
```

Do not invent their schemas prematurely.

## Deployment Direction

The existing server can run the Python application.

Likely production shape:

``` text
Internet
   ↓
HTTPS / reverse proxy
   ↓
FastAPI / Uvicorn container
   ↓
PostgreSQL
```

The public architecture may eventually resemble:

``` text
jamesdoe.com
    → Next.js website

api.jamesdoe.com
    → FastAPI domain API
```

This is a direction, not an immediate deployment requirement.

## Broader Technology-Uplift Goals

The wider learning programme expands an existing strong PHP/Laravel
background.

``` text
Python
FastAPI
SQLAlchemy
Alembic
PostgreSQL

TypeScript
Node.js
React
Next.js

later:
Kafka
GraphQL
```

Kafka and GraphQL are future learning topics, not initial JamesDoe
requirements.

## Learning Stack vs Production Requirements

A recurring principle:

**Wanting to learn a technology does not automatically mean JamesDoe V6
should use that technology in production.**

Examples:

-   learning Node.js does not require replacing FastAPI;
-   learning Kafka does not mean JamesDoe needs Kafka;
-   learning GraphQL does not mean the domain API must expose GraphQL;
-   learning another datastore does not justify creating one without a
    real requirement.

Prefer separate exercises or genuinely complementary systems when a
technology does not naturally belong in JamesDoe V6.

## Locked vs Open Decisions

### Locked / current canonical direction

``` text
Python/FastAPI is the JamesDoe domain API.
SQLAlchemy is the Python ORM.
PostgreSQL is the domain database.
Alembic manages migrations.
The core domain should not model website page structure.
React + TypeScript is the frontend learning direction.
Next.js follows React fundamentals.
The website consumes the FastAPI domain API.
Do not create a second database without a concrete requirement.
Do not replace FastAPI with Node merely because Node is being learned.
```

### Still open / deliberately undecided

``` text
Whether the website eventually needs its own CMS/database.
What datastore would support such a CMS if needed.
Whether a complementary Node.js backend/service will be built.
What that Node.js system would do.
Whether NestJS would be used.
When Kafka should enter the learning programme.
When/where GraphQL should be introduced.
Exact final deployment topology for Next.js + FastAPI.
```

A new conversation should preserve this distinction rather than treating
possibilities as decisions.

## How to Continue in a New Chat

Start a new chat in the **Coding** project and provide:

1.  `jamesdoe-v6-python-backend-foundations.md`
2.  `jamesdoe-v6-learning-handoff.md`

Then use:

> Continue my JamesDoe V6 learning programme using these two documents
> as the canonical handoff from the previous conversation. The Python
> foundations document contains the detailed backend lessons; the
> learning handoff contains the cross-stack roadmap and architectural
> context. Continue from the recorded NEXT lesson. Keep the same
> interactive teaching style: one concept at a time, practical
> exercises, PHP/Laravel comparisons where useful, and do not race ahead
> or redesign decisions already marked as locked.

At the current checkpoint:

**Continue with Lesson 12 --- Relationship Loading and the N+1
Problem.**

## Maintenance Rule

Keep these documents separate.

### `jamesdoe-v6-python-backend-foundations.md`

Contains detailed material from:

``` text
Python
FastAPI
SQLAlchemy
Alembic
Pydantic
PostgreSQL as used from Python
authentication/API implementation
Python backend architecture
```

### `jamesdoe-v6-learning-handoff.md`

Update when the **overall programme or cross-stack direction changes**,
for example:

``` text
learning sequence changes
React/Next.js direction changes
a complementary Node system is chosen
website/CMS architecture is decided
an open decision becomes locked
major project boundaries change
```

Do not duplicate every Python lesson into the handoff.

**The handoff is the map. The Python foundations document is the
detailed backend notebook.**
