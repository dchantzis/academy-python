# JamesDoe V6 --- Python & Database Foundations

## Purpose

This document is a personal refresher for the Python concepts introduced
while building JamesDoe V6.

It assumes strong PHP/Laravel and general software-engineering
knowledge, but **no prior Python knowledge**.

The goal is not to teach Python from scratch. It is to reconnect
unfamiliar Python terminology to concepts already familiar from PHP and
Laravel.

------------------------------------------------------------------------

# 1. The Stack

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

# 2. FastAPI

FastAPI is an installable **Python web framework**.

It is not part of Python itself and it is not merely a Python
convention.

Conceptually:

``` text
PHP       → Python
Laravel   → FastAPI
```

However, FastAPI is considerably less "batteries included" than Laravel.

Laravel provides or standardises things such as:

``` text
routing
Eloquent
migrations
queues
cache
authentication
validation
filesystem
Artisan
...
```

FastAPI concentrates primarily on the HTTP/API layer:

``` text
HTTP requests
routing
request parameters
validation
responses
dependency injection
OpenAPI documentation
```

We therefore choose other packages for other responsibilities:

``` text
FastAPI       → web/API framework
SQLAlchemy    → database access and ORM
Alembic       → database migrations
Psycopg       → PostgreSQL driver
```

------------------------------------------------------------------------

# 3. The FastAPI Application Object

In `app/main.py` we create the FastAPI application:

``` python
app = FastAPI(...)
```

`app` is therefore an object representing our web application.

Uvicorn currently starts the application using:

``` text
uvicorn app.main:app
```

This can be read as:

``` text
app.main:app
│   │     │
│   │     └── object named `app`
│   │
│   └── main.py module
│
└── app package
```

So Uvicorn is effectively being told:

> Find the `app` package, load the `main` module, and run the object
> named `app`.

------------------------------------------------------------------------

# 4. Python Modules

A Python `.py` file is generally called a **module**.

For example:

``` text
app/
├── main.py
└── config.py
```

`main.py` is a module.

`config.py` is another module.

If `config.py` contains:

``` python
settings = Settings()
```

then `main.py` can import it:

``` python
from app.config import settings
```

Read this almost literally:

``` text
from the `app` package
→ find the `config` module
→ import the thing named `settings`
```

------------------------------------------------------------------------

# 5. Python Packages and `__init__.py`

A directory containing related Python modules can be a **package**.

For example:

``` text
app/
├── __init__.py
├── main.py
├── config.py
└── database/
    ├── __init__.py
    └── session.py
```

Here:

``` text
app                   package
app.main              module
app.config            module

app.database          package
app.database.session  module
```

For this project, we use an `__init__.py` file to make the package
structure explicit.

The file can be completely empty.

For example:

``` text
database/
├── __init__.py
└── session.py
```

allows code to import something from `session.py` with an import such
as:

``` python
from app.database.session import get_db
```

A useful, although imperfect, PHP mental mapping is:

``` text
PHP namespace/source structure
        ≈
Python package structure
```

This will become more intuitive through repeated use rather than
memorisation.

------------------------------------------------------------------------

# 6. Python Type Annotations

Consider:

``` python
db_host: str = "database"
```

This breaks down into:

``` text
db_host       field name
: str         expected type
= "database"  default value
```

`: str` is called a **type annotation** or **type hint**.

A rough PHP equivalent would be:

``` php
public string $dbHost = 'database';
```

Other examples will include:

``` python
db_port: int = 5432
```

Here:

``` text
int → integer
str → string
```

Python itself does not always enforce type annotations at runtime.

However, libraries such as Pydantic actively use these annotations for
validation and conversion.

------------------------------------------------------------------------

# 7. Application Settings

We moved configuration into:

``` text
app/config.py
```

It currently uses Pydantic Settings:

``` python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
```

The purpose is similar to Laravel's configuration/environment system.

Our application `.env` contains values such as:

``` dotenv
APP_ENV=local

DB_HOST=database
DB_PORT=5432
DB_DATABASE=jamesdoe
DB_USER=jamesdoe
DB_PASSWORD=jamesdoe
```

Pydantic Settings allows those environment values to become Python
settings.

For example:

``` dotenv
APP_ENV=local
```

becomes accessible as:

``` python
settings.app_env
```

------------------------------------------------------------------------

# 8. `SettingsConfigDict`

We currently have:

``` python
model_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore",
)
```

This configures how Pydantic should construct our `Settings`.

## `env_file=".env"`

This means:

> Look for application configuration in the `.env` file.

## `extra="ignore"`

This means:

> If `.env` contains configuration values that are not currently
> declared by the `Settings` class, don't reject them.

For example, we currently have database variables in `.env` even before
all of them have been declared in the Python `Settings` class.

------------------------------------------------------------------------

# 9. Debug Mode

In `main.py`:

``` python
app = FastAPI(debug=settings.app_env == "local")
```

The expression:

``` python
settings.app_env == "local"
```

is a comparison.

If:

``` text
settings.app_env = "local"
```

the result is:

``` python
True
```

Therefore FastAPI effectively receives:

``` python
FastAPI(debug=True)
```

If the environment were:

``` text
production
```

the comparison would return:

``` python
False
```

and FastAPI would effectively receive:

``` python
FastAPI(debug=False)
```

A PHP-ish equivalent would be:

``` php
$app = new FastAPI(
    debug: $settings->appEnv === 'local'
);
```

------------------------------------------------------------------------

# 10. SQLAlchemy

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

# 11. Psycopg

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

# 12. Alembic

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

# 13. SQLAlchemy Engine

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

# 14. SQLAlchemy Session

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

# 15. Request-Scoped Sessions

For JamesDoe V6 we decided to use **one SQLAlchemy Session per HTTP
request**.

Conceptually:

``` text
HTTP request arrives
        ↓
create Session
        ↓
perform database work
        ↓
produce HTTP response
        ↓
close Session
```

The next HTTP request receives its own Session.

For example:

``` text
GET /artworks/123
        ↓
Session created
        ↓
Artwork queried
        ↓
JSON returned
        ↓
Session closed
```

This is the database lifecycle we have locked for the application.

------------------------------------------------------------------------

# 16. FastAPI Dependency Injection

We do not want every endpoint manually creating and cleaning up database
Sessions.

FastAPI provides **dependency injection**.

Conceptually, rather than repeatedly doing:

``` python
session = create_database_session()

# use it

session.close()
```

an endpoint can declare that it needs a database dependency.

We will eventually see code resembling:

``` python
def get_artwork(session = Depends(get_db)):
    ...
```

`Depends(get_db)` roughly means:

> FastAPI, obtain this dependency using `get_db` when handling the
> request.

Our intended lifecycle becomes:

``` text
HTTP request
    ↓
FastAPI dependency injection
    ↓
get_db creates SQLAlchemy Session
    ↓
endpoint receives Session
    ↓
endpoint performs work
    ↓
Session is cleaned up
```

This is conceptually related to Laravel resolving dependencies through
its service container, although the mechanisms are different.

------------------------------------------------------------------------

# 17. Synchronous vs Asynchronous Code

We explicitly discussed whether database access should initially be
synchronous or asynchronous.

## Synchronous

Conceptually:

``` python
artwork = get_artwork_from_database()

# execution continues after the result arrives
```

The function waits for the database operation before continuing.

This is close to the traditional Laravel/PHP mental model:

``` php
$artwork = Artwork::find($id);

echo $artwork->title;
```

## Asynchronous

Python also supports:

``` python
async def get_artwork():
    artwork = await get_artwork_from_database()
    return artwork
```

`await` means approximately:

> I need the result of this operation before this function can continue.
> Pause this function while it waits, but allow other asynchronous work
> to run.

An important correction:

``` python
artwork = await get_artwork_from_database()

# this line does NOT execute concurrently with the database operation
do_something()
```

The current function pauses at `await`.

The benefit is that the application may process unrelated work while
this request waits.

For example:

``` text
Request A
GET /artworks/123
        ↓
await database
        ↓
Request A pauses

Meanwhile:

Request B
GET /publications/coffee-and-sketch-vol-3
        ↓
can make progress
```

------------------------------------------------------------------------

# 18. Why PHP Concurrency Felt Different

Traditional Laravel applications commonly run through:

``` text
nginx / Apache
        ↓
PHP-FPM
        ↓
Laravel
```

PHP-FPM provides multiple worker processes.

For example:

``` ini
pm.max_children = 50
```

allows approximately:

``` text
Request 1  → worker 1
Request 2  → worker 2
...
Request 50 → worker 50
Request 51 → waits
```

If worker 1 is waiting for the database, it remains occupied, but
another PHP-FPM worker can handle another request.

This is why, as a Laravel developer, application-level async database
programming was not normally something that needed to be considered.

------------------------------------------------------------------------

# 19. Synchronous FastAPI Still Handles Concurrent Requests

Choosing synchronous SQLAlchemy does **not** mean:

> JamesDoe can serve only one user at a time.

FastAPI/Starlette can run synchronous blocking work through a thread
pool.

The useful conceptual comparison is:

``` text
PHP-FPM

Request A → worker
Request B → worker
Request C → worker
```

versus:

``` text
sync FastAPI

Request A → thread
Request B → thread
Request C → thread
```

The implementation is different, but the mental model is useful.

There is finite concurrency in both systems.

When capacity is exhausted, additional work waits for capacity.

------------------------------------------------------------------------

# 20. Concurrency Is Not Rate Limiting

These are different concepts.

**Concurrency capacity** answers:

> How much work can the application actively process at once?

For PHP-FPM, `pm.max_children` is an example of a concurrency control.

**Rate limiting** answers:

> How frequently is a particular client allowed to make requests?

For example:

``` text
100 requests per minute per IP
```

Async does not remove the need for rate limiting.

A client can still send excessive traffic to an asynchronous API.

------------------------------------------------------------------------

# 21. Kubernetes Is Another Scaling Layer

In a containerised PHP application:

``` text
one Kubernetes Pod
    ↓
PHP-FPM
    ↓
multiple PHP workers
```

If all PHP-FPM workers are occupied, another pod does **not
necessarily** appear automatically.

Automatic scaling requires something such as a Kubernetes Horizontal Pod
Autoscaler.

Conceptually:

``` text
traffic increases
        ↓
existing pods become heavily loaded
        ↓
autoscaling condition is reached
        ↓
Kubernetes creates another pod
        ↓
new pod becomes ready
        ↓
traffic can be distributed to it
```

Later, when traffic falls, Kubernetes may scale the number of replicas
back down.

Therefore there are several different layers of concurrency/scaling:

``` text
application concurrency
        ↓
application worker/process concurrency
        ↓
container/pod replicas
        ↓
infrastructure scaling
```

------------------------------------------------------------------------

# 22. Why We Chose Synchronous SQLAlchemy

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

# 23. Decisions Locked So Far

At the point these notes were written:

### Database

``` text
PostgreSQL 17
```

### ORM/database toolkit

``` text
SQLAlchemy 2.x
```

### Database programming model

``` text
Synchronous
```

### PostgreSQL driver

``` text
Psycopg 3
```

### Migrations

``` text
Alembic
```

### Session lifecycle

``` text
One SQLAlchemy Session per HTTP request
```

### Session provisioning

``` text
FastAPI dependency injection
```

### Initial database code location

``` text
app/
└── database/
    ├── __init__.py
    └── session.py
```

### Application configuration

Moved from:

``` text
app/main.py
```

to:

``` text
app/config.py
```

------------------------------------------------------------------------

# 24. Current Application Structure

At this point in development:

``` text
application/
└── app/
    ├── __init__.py
    ├── config.py
    ├── main.py
    └── database/
        ├── __init__.py
        └── session.py
```

`session.py` now contains the SQLAlchemy Engine, Session factory, and
request-scoped `get_db()` dependency.

------------------------------------------------------------------------

# 25. Database Settings

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

# 26. Python Functions and `def`

Python defines a function or method using `def`:

``` python
def database_url(self) -> str:
    ...
```

A rough PHP mapping is:

``` php
public function getDatabaseUrl(): string
{
    // ...
}
```

The `-> str` is the return type annotation: the function is expected to
return a string.

------------------------------------------------------------------------

# 27. `self`

Inside a Python instance method, `self` refers to the current object.

``` text
PHP          Python

$this   ≈    self
```

For example:

``` php
$this->dbHost
```

maps roughly to:

``` python
self.db_host
```

Python explicitly includes `self` in the method parameter list, but
callers do not manually pass it.

------------------------------------------------------------------------

# 28. `@property`

A normal method would be called with parentheses:

``` python
settings.database_url()
```

Adding `@property`:

``` python
@property
def database_url(self) -> str:
    ...
```

allows the calculated result to be accessed like an attribute:

``` python
settings.database_url
```

Python still executes the function when the property is accessed.

``` text
Without @property        With @property

database_url()           database_url
method                   property
```

This suits the database URL because it is a **derived value**,
calculated from the individual database settings, rather than an action.

`@property` is a Python **decorator**. We do not need to learn
decorators in depth yet; they will appear naturally again later.

------------------------------------------------------------------------

# 29. Python f-Strings

A string prefixed with `f` is a Python **formatted string literal**,
usually called an **f-string**.

``` python
name = "Dimitris"

message = f"Hello {name}"
```

produces:

``` text
Hello Dimitris
```

Without the `f`, `{name}` would remain ordinary text.

The closest familiar concept is PHP string interpolation:

``` text
PHP                         Python

"Hello {$name}"             f"Hello {name}"
"ID: {$user->id}"           f"ID: {user.id}"
```

Expressions inside `{...}` are evaluated and inserted:

``` python
price = 10
message = f"The total is {price * 2}"
```

produces:

``` text
The total is 20
```

Adjacent Python string literals are automatically joined. This lets us
split the database URL over two readable lines:

``` python
return (
    f"postgresql+psycopg://{self.db_user}:{self.db_password}"
    f"@{self.db_host}:{self.db_port}/{self.db_database}"
)
```

The two f-strings become one string.

------------------------------------------------------------------------

# 30. The Database URL Property

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

# 31. Managing Dependencies with `uv`

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

# 32. Creating the SQLAlchemy Engine

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

# 33. Connection Pooling

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

# 34. Python `with` and Context Managers

We verified the Engine manually:

``` python
with engine.connect() as connection:
    print("Connected to PostgreSQL")
```

`with` is Python syntax for using a **context manager**. A useful mental
model is:

> Obtain a resource, use it inside the indented block, and perform the
> appropriate cleanup when the block ends.

This is roughly comparable in purpose to resource acquisition combined
with `try/finally` cleanup in PHP.

Python indentation defines the block; braces are not used.

------------------------------------------------------------------------

# 35. The Session Factory

We added:

``` python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine)
```

`SessionLocal` is a configured **Session factory**, not a Session
itself.

``` text
Engine
    ↓
SessionLocal
    ↓
SessionLocal()
    ↓
new Session
```

We verified this by creating:

``` python
session = SessionLocal()
session2 = SessionLocal()
```

which produced two different Session instances. This supports our
intended lifecycle:

``` text
Request A → Session A
Request B → Session B
```

We do not share one global Session across all requests.

------------------------------------------------------------------------

# 36. `close()` and Method Calls

Calling:

``` python
session.close()
```

does not destroy the Python object. It cleans up/resets the Session's
current database resources, including releasing checked-out connections.

We also observed:

``` text
session.close     → refer to the method itself
session.close()   → call/execute the method
```

The parentheses matter. This is a general Python distinction, not a
SQLAlchemy-specific rule.

------------------------------------------------------------------------

# 37. `yield` and Generator Functions

Our request-scoped dependency is:

``` python
def get_db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
```

Compare:

``` text
return
    → provide value
    → function finishes

yield
    → provide value
    → function pauses
    → caller uses value
    → function can resume
```

A function containing `yield` is a **generator function**.

Calling:

``` python
db = get_db()
```

creates a generator object rather than immediately returning a Session.

------------------------------------------------------------------------

# 38. `next()` and `StopIteration`

We explored the generator manually.

``` python
db = get_db()
session = next(db)
```

The first `next(db)` starts `get_db()`, creates the Session, reaches
`yield session`, returns that Session, and pauses.

Calling:

``` python
next(db)
```

again resumes after `yield`, executes the `finally` block, closes the
Session, reaches the end of the generator, and raises `StopIteration`.

We do not manually use `next()` in the FastAPI application. This
experiment showed what FastAPI manages for us.

------------------------------------------------------------------------

# 39. `try` / `finally`

Python's `try` / `finally` has the same fundamental purpose as PHP's.

``` python
try:
    yield session
finally:
    session.close()
```

The `finally` block provides reliable cleanup when the dependency
finishes, including when request processing raises an exception.

------------------------------------------------------------------------

# 40. FastAPI `Depends`

An endpoint can now declare:

``` python
session: Session = Depends(get_db)
```

This combines several concepts:

``` text
session           → Python parameter name
: Session         → Python type annotation
Depends(get_db)   → FastAPI dependency injection
```

A useful reading is:

> This endpoint needs a SQLAlchemy Session, and FastAPI should obtain it
> through `get_db`.

`Depends` is FastAPI. `yield`, functions, parameters, and type
annotations are Python.

------------------------------------------------------------------------

# 41. Request-Scoped Session Lifecycle

The lifecycle we designed is now implemented:

``` text
HTTP request
    ↓
FastAPI sees Depends(get_db)
    ↓
get_db() starts
    ↓
SessionLocal()
    ↓
yield Session
    ↓
endpoint receives Session
    ↓
endpoint performs database work
    ↓
endpoint completes
    ↓
get_db() resumes
    ↓
finally
    ↓
session.close()
```

This implements the locked decision: **one SQLAlchemy Session per HTTP
request**.

------------------------------------------------------------------------

# 42. Executing SQL and SQLAlchemy Results

We verified the full database path using:

``` python
result = session.execute(text("SELECT 1"))
```

`text("SELECT 1")` explicitly represents textual SQL. The flow is:

``` text
Session
    ↓
Engine
    ↓
Psycopg
    ↓
PostgreSQL
```

`session.execute()` returned a SQLAlchemy `CursorResult` object rather
than directly returning `1`, because SQL statements can return different
numbers of rows and columns.

For this connectivity query we used:

``` python
result.scalar_one()
```

which means roughly:

> Expect exactly one scalar result and return it.

For `SELECT 1`, that scalar is the Python integer `1`.

------------------------------------------------------------------------

# 43. Application Health vs Database Health

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

# 44. Current Database Infrastructure

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

# 45. Alembic Initialization

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

# 46. Alembic Database Configuration

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

# 47. Online and Offline Migrations

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

# 48. `target_metadata`

`env.py` still contains:

``` python
target_metadata = None
```

This remains intentional. The core migrations were written explicitly.

Later, after SQLAlchemy ORM models exist, their metadata can be
connected to Alembic for migration autogeneration.

------------------------------------------------------------------------

# 49. Alembic Revisions and the Revision Chain

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

# 50. `upgrade()`, `downgrade()`, and `pass`

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

# 51. Alembic `op` and SQLAlchemy `sa`

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

# 52. SQLAlchemy Migration Type Mappings

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

# 53. Nullability, Uniqueness, and Server Defaults

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

# 54. Timestamp Convention

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

# 55. Composite Constraints and Indexes

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

# 56. Database Foreign-Key Policy

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

# 57. Application Enums and Database Comments

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

# 58. Monetary Value Convention

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

# 59. Inspecting SQL Before Applying Migrations

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

# 60. `alembic_version` vs Laravel's `migrations` Table

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

# 61. Completed Core Migration Chain

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

# 62. Where We Stopped

The explicit core-domain migration phase is complete.

``` text
Database configuration                ✓
SQLAlchemy Engine / Session            ✓
PostgreSQL connectivity               ✓
FastAPI → PostgreSQL verified         ✓

Alembic installed/configured          ✓
Online migrations                     ✓
Offline SQL generation                ✓
Revision chain understood             ✓
Upgrade/downgrade tested              ✓

11 core migrations                    ✓
11 core application tables            ✓
Indexes                               ✓
Unique/check constraints              ✓
Database comments                     ✓
TIMESTAMPTZ convention                ✓
No database-level foreign keys        ✓
No database-level cascading deletes   ✓
```

Next:

``` text
SQLAlchemy ORM models
 ↓
SQLAlchemy relationships
 ↓
Pydantic request/response models
 ↓
repositories/services where useful
 ↓
FastAPI endpoints
```

------------------------------------------------------------------------

# Quick Memory Refresh

``` text
alembic revision -m ...  → create migration/revision
revision                 → current revision ID
down_revision            → immediate parent revision
upgrade()                → move schema forward
downgrade()              → reverse revision
pass                     → Python do-nothing placeholder
op                       → Alembic operations interface
sa                       → SQLAlchemy alias

alembic upgrade head     → migrate to latest revision
alembic downgrade -1     → move back one revision
alembic upgrade head --sql
                         → generate SQL without applying
alembic current          → current database revision
alembic history          → full revision chain
alembic_version          → current position, not full history

sa.BigInteger()          → BIGINT
sa.Uuid()                → UUID
sa.String(length=n)      → VARCHAR(n)
sa.Text()                → TEXT
sa.Integer()             → INTEGER
sa.Boolean()             → BOOLEAN
sa.Date()                → DATE
sa.DateTime(timezone=True)
                         → TIMESTAMPTZ
sa.Identity(always=True) → GENERATED ALWAYS AS IDENTITY

nullable=False           → NOT NULL
nullable=True            → NULL allowed
unique=True              → UNIQUE
sa.UniqueConstraint(...) → composite UNIQUE
sa.CheckConstraint(...)  → CHECK constraint
server_default           → database-side default
op.create_index(...)     → create index
op.execute(...)          → execute raw migration SQL

created_at               → TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at               → nullable TIMESTAMPTZ
deleted_at               → nullable TIMESTAMPTZ

DB foreign keys          → deliberately not used
cross-table integrity    → application responsibility
cascading deletes        → application responsibility

price_amount             → VARCHAR(50), exact representation preserved
target_metadata          → later connects Alembic to ORM metadata
```

The next lesson begins with SQLAlchemy ORM models.
