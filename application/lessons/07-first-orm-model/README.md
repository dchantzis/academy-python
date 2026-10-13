# Lesson 07 — First Orm Model

Migrated from the original Python Backend Foundations learning notes. Original topic numbers are retained; topic order here is grouped by lesson rather than original chronology.

These notes include JamesDoe V6-specific observations from the original learning sessions; see `case-studies/jamesdoe-v6/` for their architectural context.

## Original topic 62: SQLAlchemy Declarative ORM Base

After completing the explicit migrations, we began mapping the existing
database schema into SQLAlchemy ORM models.

The common declarative base lives in:

``` text
app/database/base.py
```

and contains:

``` python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

Every ORM model inherits from this `Base`.

A useful mental model is:

``` text
Base
 ↓
shared SQLAlchemy ORM metadata
 ↓
Collection, Artwork, Product, ...
```

`Base` does not create database tables by itself. It gives SQLAlchemy a
common registry and metadata collection describing our mapped classes.

------------------------------------------------------------------------


## Original topic 63: `Mapped[...]` and `mapped_column()`

SQLAlchemy 2.x models use typed declarative mappings such as:

``` python
title: Mapped[str] = mapped_column(
    String(255),
    nullable=False,
)
```

There are several layers in this one declaration:

``` text
title
    → Python attribute name

Mapped[str]
    → ORM/Python type information

mapped_column(...)
    → SQLAlchemy column mapping

String(255)
    → database/SQL type

nullable=False
    → database NOT NULL
```

This is different from a plain Python type annotation. `Mapped[...]`
tells SQLAlchemy that the attribute participates in the ORM mapping.

A useful Laravel comparison is that an Eloquent model often relies on
database/schema conventions, whereas SQLAlchemy's typed declarative
model explicitly describes each mapped column in Python.

------------------------------------------------------------------------


## Original topic 64: Python Types vs SQLAlchemy Types

ORM declarations frequently contain both a Python-facing type and a
database-facing SQLAlchemy type.

Examples:

``` text
Python type                 SQLAlchemy type

str                         String(...)
int                         Integer / BigInteger
bool                        Boolean
datetime                    DateTime(timezone=True)
date                        Date
UUID                        Uuid
```

For example:

``` python
uuid: Mapped[UUID] = mapped_column(
    Uuid,
    nullable=False,
    unique=True,
)
```

Here:

``` text
UUID
    → Python's UUID type, imported from `uuid`

Uuid
    → SQLAlchemy's database type
```

The similar names are easy to confuse, but they belong to different
layers.

------------------------------------------------------------------------


## Original topic 65: ORM Nullability and Optional Python Values

A non-null database column is normally represented as:

``` python
title: Mapped[str] = mapped_column(
    String(255),
    nullable=False,
)
```

A nullable column is represented as:

``` python
description: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
)
```

The two sides should agree:

``` text
Mapped[str]          ↔ NOT NULL

Mapped[str | None]   ↔ NULL allowed
```

`str | None` means the Python value may be either a string or `None`.

This is Python's union-type syntax.

------------------------------------------------------------------------


## Original topic 66: ORM Identity Columns and Primary Keys

The canonical primary-key pattern used by the core models is:

``` python
id: Mapped[int] = mapped_column(
    BigInteger,
    Identity(always=True),
    primary_key=True,
)
```

This corresponds to:

``` sql
id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
```

The database generates the value when the row is inserted.

Before an ORM object has been persisted, its `id` is therefore normally
`None`, even though the mapped persisted value is an integer.

------------------------------------------------------------------------


## Original topic 67: ORM Server Defaults

The ORM models preserve the database-owned defaults already defined by
the migrations.

For example:

``` python
is_visible: Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
    server_default=true(),
)
```

and:

``` python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
    server_default=func.now(),
)
```

`server_default` means:

> PostgreSQL supplies the value when the INSERT does not provide one.

This is different from a Python-side default that would be assigned
before the INSERT reaches PostgreSQL.

Because these are server defaults, a newly constructed ORM object can
initially show values such as:

``` text
id          → None
created_at  → None
is_visible  → None
sort_order  → None
```

until persistence/refresh causes database-generated values to become
available.

------------------------------------------------------------------------


## Original topic 68: Creating an ORM Object Is Not Persisting It

We instantiated ORM objects during the first-model lesson.

For example:

``` python
collection = Collection(
    uuid=uuid4(),
    title="Coffee & Sketch",
    slug="coffee-and-sketch",
)
```

This creates a Python ORM object.

It does **not** automatically insert a row into PostgreSQL.

Conceptually:

``` text
Collection(...)
    ↓
Python object exists in memory

Session.add(...)
Session.commit(...)
    ↓
database persistence
```

The Session write lifecycle will be covered later.

We also reinforced the general Python distinction between a function
reference and a function call:

``` python
uuid4     → the function itself
uuid4()   → call the function and obtain a UUID
```

------------------------------------------------------------------------


## Original topic 69: Inspecting SQLAlchemy ORM Metadata

SQLAlchemy exposes useful introspection attributes.

For a model such as `Collection`:

``` python
Collection.__table__.columns.keys()
```

returns the mapped table column names.

The shorthand:

``` python
Collection.__table__.c.keys()
```

accesses the same columns collection.

The model's ORM mapper can be inspected with:

``` python
Collection.__mapper__.attrs.keys()
```

A particular column can be inspected with:

``` python
Collection.__table__.c.title.type
```

Useful distinction:

``` text
__table__
    → SQL/table metadata

__mapper__
    → ORM mapping metadata
```

We also reinforced that:

``` python
.keys
```

is a reference to the method, while:

``` python
.keys()
```

actually calls it.

------------------------------------------------------------------------


## Original topic 70: First ORM Model: `Collection`

`Collection` was the first complete SQLAlchemy ORM model.

It introduced the core patterns reused throughout the remaining models:

``` text
Declarative Base inheritance
Mapped[...] annotations
mapped_column(...)
BIGINT identity primary key
UUID
VARCHAR / TEXT
nullable fields
unique fields
boolean server defaults
integer server defaults
TIMESTAMPTZ
database-generated created_at
nullable updated_at
```

`cover_image_id` remains a plain `BigInteger`:

``` python
cover_image_id: Mapped[int | None] = mapped_column(
    BigInteger,
    nullable=True,
)
```

There is deliberately no SQLAlchemy `ForeignKey(...)`, matching the
project's no-database-FK policy.

The object relationship to an image will be configured separately in the
relationships lesson.

------------------------------------------------------------------------


## Original topic 71: Soft-Delete Columns in ORM Models

Models that support soft deletion contain:

``` python
deleted_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
)
```

This maps the database column only.

Unlike Laravel's `SoftDeletes` trait, merely adding `deleted_at` does
not automatically make SQLAlchemy:

``` text
exclude deleted rows
set deleted_at on delete
restore records
```

Any such behaviour must be implemented deliberately in the application
layer.

------------------------------------------------------------------------

