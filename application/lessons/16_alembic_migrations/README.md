# Lesson 16 — Alembic Database Migrations (Refresher)

**Mode:** Accelerated · 15–20 minutes  
**Prerequisites:** SQLAlchemy models, PostgreSQL basics

## Goals

- Distinguish SQLAlchemy model definitions from the actual database schema.
- Generate, review, apply, inspect and reverse Alembic migrations.
- Understand revision chains and data-preserving schema changes.

## Laravel ↔ Python

| Laravel | SQLAlchemy / Alembic |
|---|---|
| Eloquent model | SQLAlchemy ORM model |
| Migration file | Alembic revision script |
| `php artisan migrate` | `alembic upgrade head` |
| `php artisan migrate:rollback` | `alembic downgrade -1` (one revision, not one Laravel batch) |
| `php artisan migrate:status` | `alembic current` and `alembic history` |

Changing a model **does not** change the database automatically.

## Essential commands

Run these **only inside a configured Alembic project**, with its database connection and `target_metadata` set correctly:

```bash
alembic current
alembic history
alembic revision --autogenerate -m "add artwork slug"
# Inspect/edit the generated migration before running it!
alembic upgrade head
alembic downgrade -1
alembic check
```

- `revision --autogenerate`: compares SQLAlchemy metadata with the connected database and **writes a candidate revision**.
- `upgrade head`: **applies all pending revisions** up to the head.
- `downgrade -1`: reverses one revision (where supported by its downgrade function).
- `check`: reports whether autogeneration would detect pending schema operations; it does not verify migration safety.

## Example: add a slug

Suppose you update the ORM model:

```python
class Artwork(Base):
    __tablename__ = "artworks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str | None] = mapped_column(String(255), unique=True)
```

An illustrative Alembic migration might be:

```python
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.add_column("artworks", sa.Column("slug", sa.String(255), nullable=True))
    op.create_unique_constraint("uq_artworks_slug", "artworks", ["slug"])


def downgrade() -> None:
    op.drop_constraint("uq_artworks_slug", "artworks", type_="unique")
    op.drop_column("artworks", "slug")
```

**Why nullable?** Existing rows have no slug yet. To make it non-nullable safely, first backfill valid unique slugs, then add the `NOT NULL` constraint in a reviewed migration.

## Revision tracking

Alembic stores applied revision identifier(s) in `alembic_version`. Each revision declares a `revision` and `down_revision`; these form a revision graph, which may include branches.

## Critical pitfall: renames

If you rename `title` to `name` in the ORM, autogeneration may propose **drop `title` + add `name`**. That would lose existing values. Review the script and use a real rename instead:

```python
def upgrade() -> None:
    op.alter_column("artworks", "title", new_column_name="name")
```

For production, also review locking, nullability, constraints, indexes, rollback behaviour and data backfills.

## Quick knowledge check

1. Does adding a mapped column automatically change PostgreSQL? **No.**
2. `revision --autogenerate` versus `upgrade head`? **Create a candidate revision** versus **apply pending revisions**.
3. Why review a rename migration? **To avoid accidental drop/recreate and data loss.**

## Run the reference example

```bash
./dev python lessons/16_alembic_migrations/main.py
```

This script **does not connect to a database or run migrations**. It prints the Alembic workflow and safe-review reminders; real Alembic commands require a configured Alembic environment.
