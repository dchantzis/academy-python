# Lesson 06 — Database Schema And Migrations

Migrated from the original Python Backend Foundations learning notes. Original topic numbers are retained; topic order here is grouped by lesson rather than original chronology.

These notes include JamesDoe V6-specific observations from the original learning sessions; see `case-studies/jamesdoe-v6/` for their architectural context.

## Original topic 52: SQLAlchemy Migration Type Mappings

The main mappings used in the core schema are:

``` text
BIGINT                         → sa.BigInteger()
UUID                           → sa.Uuid()
VARCHAR(n)                     → sa.String(length=n)
TEXT                           → sa.Text()
INTEGER                        → sa.Integer()
BOOLEAN                        → sa.Boolean()
DATE                           → sa.Date()
TIMESTAMPTZ                    → sa.DateTime(timezone=True)
GENERATED ALWAYS AS IDENTITY   → sa.Identity(always=True)
PRIMARY KEY                    → primary_key=True
```

------------------------------------------------------------------------


## Original topic 53: Nullability, Uniqueness, and Server Defaults

Common mappings:

``` text
nullable=False       → NOT NULL
nullable=True        → NULL allowed
unique=True          → UNIQUE
```

Database-side defaults use `server_default`:

``` python
server_default=sa.true()
server_default=sa.false()
server_default=sa.text("0")
server_default=sa.text("'display'")
server_default=sa.func.now()
```

These are PostgreSQL/server defaults, not Python ORM defaults.

------------------------------------------------------------------------


## Original topic 54: Timestamp Convention

The canonical schema now uses timezone-aware timestamps:

``` sql
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMPTZ NULL,
deleted_at TIMESTAMPTZ NULL
```

SQLAlchemy represents these with:

``` python
sa.DateTime(timezone=True)
```

PostgreSQL reports the resulting type as `timestamp with time zone`.

The convention is:

``` text
created_at  → DB sets automatically on INSERT; NOT NULL
updated_at  → NULL initially; application sets on actual update
deleted_at  → NULL while active; application sets on soft delete
```

Calendar-only fields such as `artwork_date` and `publication_date`
remain `DATE`.

------------------------------------------------------------------------


## Original topic 55: Composite Constraints and Indexes

Composite uniqueness uses:

``` python
sa.UniqueConstraint("collection_id", "artwork_id")
```

Examples in the core schema include:

``` text
UNIQUE (collection_id, artwork_id)
UNIQUE (disk, path)
UNIQUE (artwork_id, image_id, role)
UNIQUE (publication_id, image_id, role)
UNIQUE (publication_group_id, publication_id)
```

The publications table also introduced:

``` python
sa.CheckConstraint(
    "volume > 0",
    name="publications_volume_positive",
)
```

Indexes are created with `op.create_index(...)`.

When a table is dropped, PostgreSQL removes its indexes too, so a
downgrade that drops the whole table does not need to drop each index
first. For a standalone index removal, Alembic supports
`op.drop_index(..., if_exists=True)`.

------------------------------------------------------------------------


## Original topic 56: Database Foreign-Key Policy

A deliberate JamesDoe V6 architecture decision:

> Cross-table referential integrity and delete behaviour are enforced
> strictly by the application, not with PostgreSQL foreign-key
> constraints.

The core schema therefore has no database-level foreign keys and no
database-level cascading deletes.

``` text
Cross-table referential integrity  → application
Delete behaviour                   → application
Cascading deletes                  → application
Foreign-key constraints            → none

PRIMARY KEY                        → database
UNIQUE                             → database
NOT NULL                           → database
Defaults                           → database where appropriate
Indexes                            → database
CHECK constraints                  → case-by-case
```

------------------------------------------------------------------------


## Original topic 57: Application Enums and Database Comments

Several string columns represent application-controlled enum values,
including:

``` text
artwork_image.role
publication_image.role
publications.publication_type
products.productable_type
products.product_type
product_variants.status
```

Their expected values are documented using PostgreSQL column comments,
executed from migrations with `op.execute(...)`.

Validation remains application-level.

------------------------------------------------------------------------


## Original topic 58: Monetary Value Convention

JamesDoe V6 deliberately stores monetary amounts as strings:

``` sql
price_amount VARCHAR(50) NOT NULL
```

Migration representation:

``` python
sa.Column(
    "price_amount",
    sa.String(length=50),
    nullable=False,
)
```

This preserves the exact representation supplied by an external
system/API. For example `"12"`, `"12.0"`, and `"12.00"` can remain
distinct representations.

When arithmetic is required, application code can parse the value into
an exact numeric representation such as Python `Decimal`.

------------------------------------------------------------------------


## Original topic 59: Inspecting SQL Before Applying Migrations

The workflow established during this lesson is:

``` text
write revision
 ↓
alembic upgrade head --sql
 ↓
inspect generated SQL
 ↓
alembic upgrade head
 ↓
verify PostgreSQL
```

We inspected column types, nullability, defaults, identity columns,
constraints, indexes, comments, TIMESTAMPTZ usage, and the deliberate
absence of foreign keys.

------------------------------------------------------------------------


## Original topic 60: `alembic_version` vs Laravel's `migrations` Table

This is an important Laravel-to-Alembic difference.

Laravel's `migrations` table records all migrations that have been
applied.

Alembic's default `alembic_version` table instead records the database's
**current position in the revision graph**.

Our database currently contains:

``` text
75421e1a25ef
```

meaning that the database is currently at that revision.

Alembic reconstructs the full history from the migration files and their
`down_revision` links.

Useful commands:

``` bash
alembic current
alembic history
```

`alembic current` shows the current database revision.

`alembic history` shows the complete revision chain.

A branched Alembic graph can have multiple active heads, so
`alembic_version` can contain more than one current revision. Our graph
is linear, so it currently contains one row.

------------------------------------------------------------------------


## Original topic 61: Completed Core Migration Chain

``` text
<base>
 ↓
d072450dc58a  collections
 ↓
9fdbc028500b  artworks
 ↓
550c9cc729c3  collection_artwork
 ↓
b5656294181a  images
 ↓
fee69049d797  artwork_image
 ↓
7b7456397e98  publications
 ↓
d846a50f1d16  publication_image
 ↓
41d75e2892a4  publication_groups
 ↓
7674cfb1be4b  publication_group_publication
 ↓
071c856606c6  products
 ↓
75421e1a25ef  product_variants (head)
```

PostgreSQL contains 11 core application tables plus Alembic's own
`alembic_version` table.

------------------------------------------------------------------------

