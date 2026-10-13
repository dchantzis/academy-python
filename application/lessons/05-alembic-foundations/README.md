# Lesson 05 — Alembic Foundations

Migrated from the original Python Backend Foundations learning notes. Original topic numbers are retained; topic order here is grouped by lesson rather than original chronology.

These notes include JamesDoe V6-specific observations from the original learning sessions; see `case-studies/jamesdoe-v6/` for their architectural context.

## Original topic 12: Alembic

Alembic is the migration system commonly used with SQLAlchemy.

Think:

``` text
Laravel migrations / Phinx
        ≈
Alembic
```

The conceptual equivalent of:

``` bash
php artisan migrate
```

is:

``` bash
alembic upgrade head
```

JamesDoe V6 will eventually expose this through our existing development
helper:

``` bash
./dev db migrate
```

Alembic has now been initialized for JamesDoe V6. The practical setup is
documented later in this refresher.

------------------------------------------------------------------------


## Original topic 45: Alembic Initialization

Alembic has now been initialized for JamesDoe V6 using:

``` bash
alembic init alembic
```

This created:

``` text
application/
├── alembic.ini
└── alembic/
    ├── README
    ├── env.py
    ├── script.py.mako
    └── versions/
```

The important parts for now are:

``` text
alembic.ini
    → Alembic's main configuration file

alembic/env.py
    → Python environment Alembic runs when executing migrations

alembic/versions/
    → migration files will live here
```

A rough Laravel mapping is:

``` text
Laravel                         Alembic

database/migrations/       ≈   alembic/versions/
migration configuration    ≈   alembic.ini + alembic/env.py
```

We do not need to understand `script.py.mako` yet.

------------------------------------------------------------------------


## Original topic 46: Alembic Database Configuration

Alembic initially generated this placeholder in `alembic.ini`:

``` ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

The generated `env.py` normally obtains this using:

``` python
config.get_main_option("sqlalchemy.url")
```

However, JamesDoe V6 already has a database configuration path:

``` text
.env
    ↓
Pydantic Settings
    ↓
settings.database_url
    ↓
SQLAlchemy Engine
```

We do not want to duplicate the real database URL or credentials inside
`alembic.ini`.

For online migrations, Alembic therefore imports the application's
existing Engine:

``` python
from app.database.session import engine
```

and uses:

``` python
connectable = engine
```

instead of creating another Engine from the configuration in
`alembic.ini`.

The resulting architecture is:

``` text
.env
    ↓
Settings
    ↓
settings.database_url
    ↓
SQLAlchemy Engine
    ├── FastAPI
    └── Alembic
```

FastAPI and Alembic therefore share the same database configuration
source.

------------------------------------------------------------------------


## Original topic 47: Online and Offline Migrations

Alembic supports both online and offline migration modes.

Normal execution:

``` bash
alembic upgrade head
```

uses online mode and applies migrations to PostgreSQL.

Offline mode:

``` bash
alembic upgrade head --sql
```

generates the SQL without applying it. We used this repeatedly to
inspect each migration before execution.

Offline mode does not inspect the live database's current revision. With
no explicit starting revision, it generates SQL from `<base>` through
`head`.

To keep both modes on the same configuration source, `env.py` uses:

``` python
config.set_main_option("sqlalchemy.url", settings.database_url)
```

So both migration paths ultimately use the application's `.env` /
Pydantic settings rather than duplicated credentials in `alembic.ini`.

------------------------------------------------------------------------


## Original topic 48: `target_metadata`

`env.py` still contains:

``` python
target_metadata = None
```

This remains intentional. The core migrations were written explicitly.

Later, after SQLAlchemy ORM models exist, their metadata can be
connected to Alembic for migration autogeneration.

------------------------------------------------------------------------


## Original topic 49: Alembic Revisions and the Revision Chain

Alembic calls each migration a **revision**:

``` bash
alembic revision -m "create table collections"
```

Each revision contains identifiers such as:

``` python
revision = "9fdbc028500b"
down_revision = "d072450dc58a"
```

`revision` identifies the current migration. `down_revision` identifies
its immediate parent. The first migration has `down_revision = None`.

This creates an explicit chain:

``` text
<base>
 ↓
collections
 ↓
artworks
 ↓
...
 ↓
product_variants (head)
```

Alembic identifies migrations by revision IDs, not filenames. Long
filenames may be truncated, and a migration file can be renamed without
changing its identity as long as its revision metadata remains correct.

------------------------------------------------------------------------


## Original topic 50: `upgrade()`, `downgrade()`, and `pass`

Every revision contains:

``` python
def upgrade() -> None:
    ...

def downgrade() -> None:
    ...
```

`upgrade()` moves the schema forward. `downgrade()` reverses that
revision.

An empty generated function initially contains:

``` python
pass
```

`pass` means "do nothing" and keeps an empty Python block valid.

We tested migration rollback with:

``` bash
alembic downgrade -1
```

and then reapplied it with:

``` bash
alembic upgrade head
```

------------------------------------------------------------------------


## Original topic 51: Alembic `op` and SQLAlchemy `sa`

Migration files use:

``` python
from alembic import op
import sqlalchemy as sa
```

`op` is Alembic's schema-operations interface:

``` python
op.create_table(...)
op.drop_table(...)
op.create_index(...)
op.drop_index(...)
op.execute(...)
```

`sa` is simply an alias for SQLAlchemy.

`op.execute(...)` lets a migration execute raw SQL. We used it for
PostgreSQL column comments.

------------------------------------------------------------------------

