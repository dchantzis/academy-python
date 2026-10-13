# Lesson 03 — Database Infrastructure

Migrated from the original Python Backend Foundations learning notes. Original topic numbers are retained; topic order here is grouped by lesson rather than original chronology.

These notes include JamesDoe V6-specific observations from the original learning sessions; see `case-studies/jamesdoe-v6/` for their architectural context.

## Original topic 1: The Stack

The planned JamesDoe V6 backend stack is:

``` text
FastAPI
    ↓
SQLAlchemy 2.x
    ↓
Psycopg 3
    ↓
PostgreSQL 17
```

Database migrations will be handled by:

``` text
Alembic
    ↓
PostgreSQL
```

The rough PHP/Laravel mapping is:

  PHP / Laravel                          Python / JamesDoe V6
  -------------------------------------- ------------------------
  PHP                                    Python
  Laravel                                FastAPI
  Composer                               uv
  `composer.json`                        `pyproject.toml`
  Eloquent ORM                           SQLAlchemy ORM
  Laravel DB connection infrastructure   SQLAlchemy Engine
  Eloquent query/save lifecycle          SQLAlchemy Session
  PDO / `pdo_pgsql`                      Psycopg
  Laravel migrations / Phinx             Alembic
  `php artisan migrate`                  `alembic upgrade head`
  PHPUnit                                pytest

These are conceptual equivalents, not necessarily exact one-to-one
implementations.

------------------------------------------------------------------------


## Original topic 10: SQLAlchemy

SQLAlchemy is the database toolkit/ORM selected for JamesDoe V6.

The easiest initial mental mapping is:

``` text
Eloquent ORM
    ≈
SQLAlchemy ORM
```

It will provide our Python representations of database entities and
allow us to query and modify database data.

For example, something conceptually similar to:

``` php
$artwork = Artwork::find(123);
```

may eventually look roughly like:

``` python
artwork = session.get(Artwork, 123)
```

Do not expect SQLAlchemy to behave exactly like Eloquent.

The mapping is intended to provide an initial mental anchor.

------------------------------------------------------------------------


## Original topic 11: Psycopg

SQLAlchemy does not itself speak directly to PostgreSQL.

It uses a PostgreSQL **driver**.

For JamesDoe V6 we chose:

``` text
Psycopg 3
```

Therefore:

``` text
SQLAlchemy
    ↓
Psycopg
    ↓
PostgreSQL
```

The rough PHP equivalent is:

``` text
Laravel/Eloquent
    ↓
PDO / pdo_pgsql
    ↓
PostgreSQL
```

Other Python PostgreSQL drivers exist, including:

``` text
asyncpg
pg8000
psycopg2
```

We chose modern Psycopg 3.

If we later encounter:

``` text
postgresql+psycopg://...
```

the `+psycopg` portion means:

> SQLAlchemy should use Psycopg as the PostgreSQL driver.

------------------------------------------------------------------------


## Original topic 13: SQLAlchemy Engine

The SQLAlchemy **Engine** represents the application's configured
gateway to the database.

It knows how the application should reach PostgreSQL:

``` text
database type
driver
host
port
database
username
password
```

For JamesDoe V6 that means information such as:

``` text
PostgreSQL
Psycopg
database
5432
jamesdoe
...
```

The closest useful Laravel mental model is:

``` text
config/database.php
        ↓
Laravel configured DB connection

            ≈

SQLAlchemy Engine configuration
        ↓
SQLAlchemy Engine
```

Eventually we will encounter something like:

``` python
engine = create_engine(...)
```

A useful translation when first seeing this is:

> Set up the application's database connection infrastructure.

The Engine is long-lived application infrastructure.

------------------------------------------------------------------------


## Original topic 14: SQLAlchemy Session

The Engine is not what normal application code will generally use
directly to perform ORM work.

For that we use a SQLAlchemy **Session**.

Initial mental model:

``` text
Engine
    =
database connection infrastructure

Session
    =
a unit of database work
```

For example:

``` python
artwork = session.get(Artwork, 123)
```

A Session can participate in:

``` text
queries
inserts
updates
deletes
transactions
```

It should not be thought of as a permanent database connection.

The Engine manages the underlying connection infrastructure.

Sessions are shorter-lived objects which use that infrastructure.

------------------------------------------------------------------------


## Original topic 22: Why We Chose Synchronous SQLAlchemy

JamesDoe V6 is expected initially to have requests such as:

``` text
GET /artworks
GET /artworks/{slug}
GET /collections/{slug}
GET /publications/{slug}
GET /products/{slug}
```

Typical work:

``` text
receive HTTP request
        ↓
perform relatively fast PostgreSQL query
        ↓
construct JSON response
        ↓
return
```

There currently isn't a strong requirement for requests that spend long
periods waiting for multiple external services.

Async would therefore introduce additional concepts:

``` text
async
await
AsyncSession
async database engine
async driver behaviour
```

without a clear performance requirement.

We therefore locked:

> **JamesDoe V6 will initially use SQLAlchemy 2.x synchronous database
> access.**

This is not because async is bad.

It is because synchronous database access fits the current workload and
provides a simpler implementation.

Async can be introduced later where there is an actual requirement.

------------------------------------------------------------------------


## Original topic 25: Database Settings

The database configuration is now represented in the Pydantic `Settings`
class:

``` python
class Settings(BaseSettings):
    app_env: str = "local"

    db_host: str = "database"
    db_port: int = 5432
    db_database: str = "jamesdoe"
    db_user: str = "jamesdoe"
    db_password: str
```

The first four database settings have sensible local-development
defaults.

The password deliberately does **not** have a default:

``` python
db_password: str
```

This means:

> A string value for `DB_PASSWORD` must be supplied externally; there is
> no password embedded in the Python source code.

For local development, that value is supplied by the application's
`.env` file.

## Why `db_host` is `database`

The value:

``` python
db_host: str = "database"
```

comes from the Docker Compose service name:

``` yaml
services:
  app:
    # ...

  database:
    image: postgres:17
```

Docker Compose provides internal DNS on the Compose network, so the
`app` container can reach PostgreSQL using the service name `database`
as its hostname.

Conceptually:

``` text
app container
    ↓
database:5432
    ↓
PostgreSQL container
```

This is why the FastAPI application does **not** connect to
`localhost:54329`. Inside the `app` container, `localhost` refers to the
app container itself.

``` text
Ubuntu host                  Docker network

localhost:54329  ───────→    database:5432
                               ↑
                               FastAPI uses this
```

This is a Docker/Compose concept, not a Python or FastAPI convention.

------------------------------------------------------------------------


## Original topic 30: The Database URL Property

The `Settings` class now exposes the SQLAlchemy database URL as a
calculated property:

``` python
@property
def database_url(self) -> str:
    return (
        f"postgresql+psycopg://{self.db_user}:{self.db_password}"
        f"@{self.db_host}:{self.db_port}/{self.db_database}"
    )
```

Application code can therefore access:

``` python
settings.database_url
```

rather than rebuilding the connection string in multiple places.

The URL structure is:

``` text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

and:

``` text
postgresql+psycopg
```

means PostgreSQL using the Psycopg driver.

This property forms the bridge between application configuration and the
SQLAlchemy Engine we will create next.

------------------------------------------------------------------------


## Original topic 31: Managing Dependencies with `uv`

The database packages are now installed using:

``` bash
uv add "sqlalchemy>=2.0,<2.1"
uv add "psycopg[binary]>=3,<4"
uv add "alembic>=1.18,<2"
```

The resolved versions at this point are SQLAlchemy 2.0.53, Psycopg
3.3.5, and Alembic 1.20.0.

``` text
Composer                 uv
composer require         uv add
composer.json            pyproject.toml
composer.lock            uv.lock
```

`pyproject.toml` records our direct project requirements. `uv.lock`
records the complete resolved dependency graph. Packages such as
`greenlet`, `psycopg-binary`, `mako`, and `markupsafe` appeared as
dependencies required underneath the packages we deliberately added.

------------------------------------------------------------------------


## Original topic 32: Creating the SQLAlchemy Engine

The database infrastructure in `app/database/session.py` begins with:

``` python
from sqlalchemy import create_engine
from app.config import settings

engine = create_engine(settings.database_url)
```

The flow is:

``` text
settings.database_url
    ↓
create_engine(...)
    ↓
SQLAlchemy Engine
    ↓
Psycopg
    ↓
PostgreSQL
```

The Engine is long-lived database infrastructure. `create_engine()` does
not mean "open one permanent PostgreSQL connection now." Connections are
obtained when database work actually needs them.

------------------------------------------------------------------------


## Original topic 33: Connection Pooling

The Engine normally manages database connections through a connection
pool:

``` text
FastAPI
    ↓
Engine
    ↓
Connection Pool
  ┌─┼─┐
  ↓ ↓ ↓
 connections
  ↓ ↓ ↓
PostgreSQL
```

Important distinction:

``` text
Engine      → long-lived database infrastructure
Connection  → actual PostgreSQL connection
Session     → unit of ORM/database work using Engine resources
```

A connection can be borrowed for database work and released back to the
pool for reuse.

------------------------------------------------------------------------


## Original topic 43: Application Health vs Database Health

We restored the original application health endpoint:

``` python
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

Its responsibility is simply:

``` text
Is the FastAPI application responding?
```

We added a separate database-aware check:

``` python
@app.get("/check-db-session")
def check_db_session(session: Session = Depends(get_db)) -> dict[str, str]:
    result = session.execute(text("SELECT 1"))
    result.scalar_one()

    return {"status": "ok"}
```

Its responsibility is:

``` text
FastAPI
    ↓
get_db()
    ↓
SQLAlchemy Session
    ↓
Engine
    ↓
Psycopg
    ↓
PostgreSQL
```

Keeping these checks separate means the basic application health
endpoint does not depend on database availability.

------------------------------------------------------------------------


## Original topic 44: Current Database Infrastructure

The current `app/database/session.py` is:

``` python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(bind=engine)


def get_db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
```

The complete path is now:

``` text
Pydantic Settings
    ↓
settings.database_url
    ↓
SQLAlchemy Engine
    ↓
connection pool
    ↓
SessionLocal
    ↓
request-specific Session
    ↓
FastAPI Depends(get_db)
    ↓
endpoint database work
    ↓
Session cleanup
```

This path has been verified against the running PostgreSQL 17 container.

------------------------------------------------------------------------

