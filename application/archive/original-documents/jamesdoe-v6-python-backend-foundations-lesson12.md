# JamesDoe V6 --- Python Backend Foundations

## Purpose

This document is a living learning and reference companion for the
Python backend of JamesDoe V6.

It records the Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL, ORM,
and API concepts introduced while building the application, together
with the architectural decisions made along the way.

It assumes strong PHP/Laravel and general software-engineering
knowledge, but **no prior Python knowledge**.

The goal is not to teach programming from scratch. It is to reconnect
unfamiliar Python terminology and ecosystem concepts to ideas already
familiar from PHP and Laravel, while preserving the practical lessons
learned while implementing JamesDoe V6.

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

# 62. SQLAlchemy Declarative ORM Base

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

# 63. `Mapped[...]` and `mapped_column()`

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

# 64. Python Types vs SQLAlchemy Types

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

# 65. ORM Nullability and Optional Python Values

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

# 66. ORM Identity Columns and Primary Keys

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

# 67. ORM Server Defaults

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

# 68. Creating an ORM Object Is Not Persisting It

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

# 69. Inspecting SQLAlchemy ORM Metadata

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

# 70. First ORM Model: `Collection`

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

# 71. Soft-Delete Columns in ORM Models

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

# 72. Association Models

Several many-to-many relationships use explicit association tables,
including:

``` text
collection_artwork
publication_group_publication
```

Rather than treating them as invisible pivot tables, we map them as ORM
classes because they contain their own data, including `sort_order` and
timestamps.

For example:

``` python
class CollectionArtwork(Base):
    __tablename__ = "collection_artwork"

    collection_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    artwork_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
```

A rough Laravel comparison is an explicit pivot model rather than only
using an implicit `belongsToMany` pivot table.

------------------------------------------------------------------------

# 73. ORM `UniqueConstraint`

Composite uniqueness is represented at model level using
`UniqueConstraint`.

For example:

``` python
__table_args__ = (
    UniqueConstraint("collection_id", "artwork_id"),
)
```

This means the **pair** must be unique.

It does not mean each column must individually be unique.

``` text
collection_id   artwork_id

1               10    ✓
1               11    ✓
2               10    ✓
1               10    ✗ duplicate pair
```

This also reinforced a Python tuple rule:

``` python
(value,)
```

is a one-element tuple.

Parentheses alone do not create a tuple; the trailing comma does.

Other mapped composite unique constraints include:

``` text
images
    → disk + path

artwork_image
    → artwork_id + image_id + role

publication_image
    → publication_id + image_id + role

publication_group_publication
    → publication_group_id + publication_id
```

------------------------------------------------------------------------

# 74. ORM `CheckConstraint`

`Publication` maps the database rule:

``` sql
CHECK (volume > 0)
```

using:

``` python
__table_args__ = (
    CheckConstraint("volume > 0"),
)
```

Because `volume` itself is nullable:

``` text
NULL        → allowed
1, 2, 3... → allowed
0, -1...   → rejected by the database
```

This is an example of a local row invariant that remains useful to
enforce at database level even though cross-table referential integrity
is application-owned.

------------------------------------------------------------------------

# 75. Application-Level Enum-Like Strings in ORM Models

Columns such as:

``` text
artwork_image.role
publication_image.role
publications.publication_type
products.productable_type
products.product_type
product_variants.status
```

remain ordinary SQLAlchemy `String(...)` columns.

For example:

``` python
status: Mapped[str] = mapped_column(
    String(50),
    nullable=False,
    server_default="active",
)
```

Expected values can be documented in code:

``` python
# draft | active | sold | out_of_stock | archived
```

but SQLAlchemy/PostgreSQL are not currently modelling these as database
enum types.

Validation remains an application responsibility and will become more
explicit as the Pydantic/application layers are built.

------------------------------------------------------------------------

# 76. Image Attachment Models and Roles

Artwork and publication images use explicit attachment models:

``` text
ArtworkImage
PublicationImage
```

Each records:

``` text
parent entity ID
image ID
role
sort_order
is_primary
timestamps
```

For `ArtworkImage`, the unique combination is:

``` text
artwork_id + image_id + role
```

This deliberately allows the same image to be attached to the same
artwork under different roles.

The same pattern applies to publication images.

The scalar attachment IDs are now complemented by explicit ORM
relationships for `ArtworkImage`. Equivalent attachment relationships
can follow the same pattern.

------------------------------------------------------------------------

# 77. Explicit and Composite ORM Indexes

A simple single-column index can be declared on a mapped column using:

``` python
index=True
```

For example:

``` python
artwork_id: Mapped[int] = mapped_column(
    BigInteger,
    nullable=False,
    index=True,
)
```

SQLAlchemy will generate an index name automatically in its metadata.

When an existing migration has an important explicit name, or when the
index spans multiple columns, we can instead use `Index(...)`.

For example, `Product` has:

``` python
__table_args__ = (
    Index(
        "products_productable_idx",
        "productable_type",
        "productable_id",
    ),
)
```

This maps the existing database index:

``` sql
CREATE INDEX products_productable_idx
ON products (productable_type, productable_id);
```

A useful distinction:

``` text
index=True
    → convenient single-column index

Index("name", "a", "b")
    → explicit named index; can span multiple columns
```

Using explicit names also helps keep ORM metadata aligned with the names
already created by migrations.

------------------------------------------------------------------------

# 78. Polymorphic Product References

`Product` introduced an important domain pattern:

``` text
productable_type
productable_id
```

For example:

``` text
productable_type = "artwork"
productable_id   = 72
```

means:

``` text
artworks.id = 72
```

while:

``` text
productable_type = "publication"
productable_id   = 72
```

means:

``` text
publications.id = 72
```

Therefore `productable_id` has no complete meaning by itself.

The logical reference is the pair:

``` text
(productable_type, productable_id)
```

The same numeric ID can legitimately exist in both target tables.

This is also why a conventional database foreign key cannot directly
describe this polymorphic reference: the target table depends on the
value of `productable_type`.

Existence and type correctness are therefore application-layer
responsibilities.

------------------------------------------------------------------------

# 79. Why the Product Polymorphic Index Is Composite

Products are indexed by:

``` text
productable_type + productable_id
```

rather than only by `productable_id`.

The ORM declaration is:

``` python
Index(
    "products_productable_idx",
    "productable_type",
    "productable_id",
)
```

This reflects how the reference is actually interpreted.

Conceptually, queries are interested in combinations such as:

``` text
"artwork", 72
"publication", 72
```

rather than the ambiguous value `72` alone.

------------------------------------------------------------------------

# 80. `ProductVariant` and Exact Monetary Strings

`ProductVariant` preserves the locked monetary design:

``` python
price_amount: Mapped[str] = mapped_column(
    String(50),
    nullable=False,
)
```

It is deliberately **not** mapped as:

``` text
float
Decimal
Numeric
```

because the database stores the exact external representation as a
string.

The ORM model should faithfully map the canonical database schema rather
than silently redesign it.

If calculations are required later, application code can parse the
string into an exact numeric representation such as `Decimal`.

------------------------------------------------------------------------

# 81. Product Variant Stock and Status Semantics

Important `ProductVariant` fields include:

``` text
quantity
    → nullable integer for depletable physical stock

is_unlimited
    → boolean indicating non-depleting/unlimited stock

status
    → application-controlled lifecycle value

is_default
    → identifies the default variant for a product
```

Expected status values are:

``` text
draft
active
sold
out_of_stock
archived
```

`quantity` may be `NULL` when stock quantity is not applicable, such as
an unlimited digital product.

These semantics belong to the application/domain layer; the ORM model
maps the underlying columns.

------------------------------------------------------------------------

# 82. Multiple Explicit Indexes on `ProductVariant`

`ProductVariant` maps three existing indexes:

``` python
__table_args__ = (
    Index(
        "product_variants_product_idx",
        "product_id",
    ),
    Index(
        "product_variants_default_idx",
        "product_id",
        "is_default",
    ),
    Index(
        "product_variants_status_idx",
        "status",
    ),
)
```

These correspond to:

``` text
product_variants_product_idx
    → product_id

product_variants_default_idx
    → product_id + is_default

product_variants_status_idx
    → status
```

Even the single-column indexes are expressed explicitly here so their
ORM metadata names match the already-existing migration names.

------------------------------------------------------------------------

# 83. Completed Core ORM Models

The complete core-domain model set is now:

``` text
Collection
Artwork
CollectionArtwork
Image
ArtworkImage
Publication
PublicationImage
PublicationGroup
PublicationGroupPublication
Product
ProductVariant
```

That is:

``` text
11 core database tables
        ↕
11 SQLAlchemy ORM models
```

The models now describe columns, types, nullability, defaults,
constraints, and indexes.

The model set now also includes the first object-to-object
relationships; relationship configuration is documented in Lesson 9
below.

------------------------------------------------------------------------

# 84. ORM Models Do Not Require Database Foreign Keys

The project still deliberately has no PostgreSQL foreign-key
constraints.

That does not prevent us from using SQLAlchemy ORM relationships.

The important distinction is:

``` text
Database foreign key
    → PostgreSQL enforces cross-table referential integrity

ORM relationship
    → SQLAlchemy understands how Python objects relate
```

Because our columns do not contain `ForeignKey(...)` metadata,
SQLAlchemy cannot automatically infer all of the joins.

We therefore configure relevant joins explicitly with `relationship()`,
`primaryjoin`, and `foreign()`.

For example, SQLAlchemy currently sees:

``` text
ProductVariant.product_id
```

as a `BIGINT` value.

Lesson 9 now configures object access such as:

``` python
product.variants
variant.product
```

without introducing PostgreSQL foreign-key constraints.

------------------------------------------------------------------------

# 85. Current ORM Inspection Workflow

The smoke-test workflow used while creating models is:

``` python
from app.models.product_variant import ProductVariant

ProductVariant.__table__.columns.keys()
ProductVariant.__table__.c.keys()
ProductVariant.__mapper__.attrs.keys()
ProductVariant.__table__.indexes
```

These checks answer different questions:

``` text
columns.keys()
    → what columns does SQLAlchemy think the table has?

c.keys()
    → shorthand for the same columns collection

__mapper__.attrs.keys()
    → what attributes are mapped by the ORM?

__table__.indexes
    → what indexes are represented in model metadata?
```

This provided a quick way to compare each ORM model against the already
applied migration/schema.

------------------------------------------------------------------------

# 86. Lesson 9: ORM Relationships Without Database Foreign Keys

Lesson 9 introduced SQLAlchemy object relationships while preserving the
project's deliberate policy of having no PostgreSQL foreign-key
constraints.

The key distinction is:

``` text
Database foreign key
    → PostgreSQL referential-integrity constraint

SQLAlchemy relationship
    → ORM description of how Python objects relate
```

Because the mapped ID columns do not use `ForeignKey(...)`, SQLAlchemy
cannot infer the join direction automatically. Relationships therefore
use explicit `primaryjoin` expressions together with `foreign()`.

------------------------------------------------------------------------

# 87. `relationship()` and Relationship Cardinality

SQLAlchemy's `relationship()` maps an object-to-object relationship.

For example, `Product` now has:

``` python
variants: Mapped[list["ProductVariant"]] = relationship(
    "ProductVariant",
    primaryjoin="Product.id == foreign(ProductVariant.product_id)",
    back_populates="product",
)
```

Unlike `mapped_column()`, this does not represent another database
column.

The type annotation expresses cardinality:

``` text
Mapped[list["ProductVariant"]] → collection relationship / one-to-many
Mapped["Product"]              → scalar relationship / many-to-one
```

SQLAlchemy exposes this through `uselist`:

``` python
Product.__mapper__.relationships["variants"].uselist
# True

ProductVariant.__mapper__.relationships["product"].uselist
# False
```

------------------------------------------------------------------------

# 88. Explicit `primaryjoin` and `foreign()`

With conventional SQLAlchemy `ForeignKey(...)` metadata, SQLAlchemy can
normally infer how mapped tables should be joined. JamesDoe V6
deliberately does not use that metadata.

We therefore state the join explicitly:

``` python
primaryjoin="Product.id == foreign(ProductVariant.product_id)"
```

The underlying relationship is:

``` text
Product.id
    ↑
    │
ProductVariant.product_id
```

`primaryjoin` describes how the rows relate. `foreign()` identifies
`ProductVariant.product_id` as the referencing side.

This is ORM configuration only. It does not create a PostgreSQL
`FOREIGN KEY` constraint.

------------------------------------------------------------------------

# 89. Bidirectional Relationships and `back_populates`

The Product relationship is configured in both directions.

`Product`:

``` python
variants: Mapped[list["ProductVariant"]] = relationship(
    "ProductVariant",
    primaryjoin="Product.id == foreign(ProductVariant.product_id)",
    back_populates="product",
)
```

`ProductVariant`:

``` python
product: Mapped["Product"] = relationship(
    "Product",
    primaryjoin="foreign(ProductVariant.product_id) == Product.id",
    back_populates="variants",
)
```

`back_populates` names the relationship attribute on the other mapped
class:

``` text
Product.variants
      ↕
ProductVariant.product
```

It also keeps both sides synchronized in Python memory. For example:

``` python
product.variants.append(variant)
```

makes:

``` python
variant.product is product
```

true without separately assigning `variant.product = product`.

------------------------------------------------------------------------

# 90. ORM Relationship State vs ID Column State

We connected unpersisted objects through the ORM:

``` python
product.variants.append(variant)
```

Before persistence, PostgreSQL has not generated the Product identity
value:

``` text
product.id          → None
variant.product_id  → None
```

Nevertheless:

``` python
variant.product is product
```

is already true.

This demonstrates:

``` text
product.variants / variant.product
    → relationship between Python ORM objects

variant.product_id
    → mapped database column
```

SQLAlchemy can know that two in-memory objects are related before the
database-generated primary key exists. The persistence/flush lifecycle
will be covered later.

------------------------------------------------------------------------

# 91. Association Models and Relationships

`CollectionArtwork` is an explicit association model rather than an
invisible many-to-many pivot table:

``` text
Collection 1 ───── * CollectionArtwork * ───── 1 Artwork
```

The relationships are:

``` text
Collection.collection_artworks  → list[CollectionArtwork]
CollectionArtwork.collection    → Collection
Artwork.collection_artworks     → list[CollectionArtwork]
CollectionArtwork.artwork       → Artwork
```

For example:

``` python
collection_artworks: Mapped[list["CollectionArtwork"]] = relationship(
    "CollectionArtwork",
    primaryjoin="Collection.id == foreign(CollectionArtwork.collection_id)",
    back_populates="collection",
)
```

with the reverse:

``` python
collection: Mapped["Collection"] = relationship(
    "Collection",
    primaryjoin="foreign(CollectionArtwork.collection_id) == Collection.id",
    back_populates="collection_artworks",
)
```

The association object remains visible because the relationship itself
contains domain data such as `sort_order` and timestamps.

We have not added a direct `collection.artworks` convenience
relationship at this stage.

------------------------------------------------------------------------

# 92. Artwork Image Association Relationships

`ArtworkImage` follows the same association-model pattern:

``` text
Artwork 1 ───── * ArtworkImage * ───── 1 Image
```

The resulting relationships are:

``` text
Artwork.artwork_images   → list[ArtworkImage]
ArtworkImage.artwork     → Artwork
Image.artwork_images     → list[ArtworkImage]
ArtworkImage.image       → Image
```

The logical joins are:

``` text
Artwork.id = ArtworkImage.artwork_id
Image.id   = ArtworkImage.image_id
```

For example, the Image side is:

``` python
artwork_images: Mapped[list["ArtworkImage"]] = relationship(
    "ArtworkImage",
    primaryjoin="Image.id == foreign(ArtworkImage.image_id)",
    back_populates="image",
)
```

and the reverse is:

``` python
image: Mapped["Image"] = relationship(
    "Image",
    primaryjoin="foreign(ArtworkImage.image_id) == Image.id",
    back_populates="artwork_images",
)
```

The explicit association object is useful because an attachment carries
its own data: `role`, `sort_order`, `is_primary`, and timestamps.

The repeated association pattern is now understood and does not need a
separate learning lesson for every equivalent association table.

------------------------------------------------------------------------

# 93. String Relationship Targets and the Declarative Registry

Relationship targets are currently referred to by strings:

``` python
relationship("ProductVariant", ...)
relationship("CollectionArtwork", ...)
relationship("ArtworkImage", ...)
```

This helps avoid direct imports between related model modules and the
circular-import problems those imports can create.

However, a string target can only be resolved after its mapped class has
been imported and registered with the common `Base`.

We inspected:

``` python
list(Product.registry._class_registry.keys())
```

Before importing `ProductVariant`, only `Product` and SQLAlchemy's
internal registry entry were present. After importing `ProductVariant`,
that class appeared in the registry.

The important rule is:

``` text
Python file exists
    ≠
mapped class has been registered

module imported
    ↓
class definition executes
    ↓
class inherits Base
    ↓
SQLAlchemy registers mapped class
```

------------------------------------------------------------------------

# 94. Partial Imports and Mapper Configuration

After adding relationships to `Artwork`, a fresh interpreter imported
`Artwork`, `ArtworkImage`, and `Image`, but not `CollectionArtwork`.

Inspecting `Artwork.__mapper__.relationships` caused mapper
configuration to fail while resolving:

``` python
"Artwork.id == foreign(CollectionArtwork.artwork_id)"
```

because `CollectionArtwork` had not yet been registered.

Importing the complete related model graph allowed mapper configuration
to succeed.

String relationship declarations therefore avoid direct circular
imports, but they do not remove the need for all mapped classes to be
loaded before the complete mapper graph is configured.

------------------------------------------------------------------------

# 95. Central Model Registration

`app/models/__init__.py` now acts as the central model-registration
point and imports all 11 mapped classes:

``` python
from app.models.artwork import Artwork
from app.models.artwork_image import ArtworkImage
from app.models.collection import Collection
from app.models.collection_artwork import CollectionArtwork
from app.models.image import Image
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.publication import Publication
from app.models.publication_group import PublicationGroup
from app.models.publication_group_publication import PublicationGroupPublication
from app.models.publication_image import PublicationImage
```

Therefore:

``` python
import app.models
```

loads every model module and registers all mapped classes with the
common declarative registry.

These imports have an intentional registration side effect even when the
imported class names are not otherwise referenced by `__init__.py`.

------------------------------------------------------------------------

# 96. Verifying the Complete Model Registry

After:

``` python
import app.models
from app.database.base import Base
```

we verified:

``` python
list(Base.registry._class_registry.keys())
```

and obtained all 11 application models:

``` text
Artwork
ArtworkImage
Collection
CollectionArtwork
Image
Product
ProductVariant
Publication
PublicationGroup
PublicationGroupPublication
PublicationImage
```

plus SQLAlchemy's internal `_sa_module_registry`.

------------------------------------------------------------------------

# 97. `configure_mappers()` as a Sanity Check

SQLAlchemy provides:

``` python
from sqlalchemy.orm import configure_mappers

configure_mappers()
```

This forces configuration of the registered mapper graph.

After central model registration, `configure_mappers()` completed
without an exception.

This verifies that SQLAlchemy can resolve and configure the
relationships currently added to the model graph. It is a useful sanity
check after relationship changes because mapper configuration may
otherwise happen lazily.

------------------------------------------------------------------------

# 98. Lesson 9 Checkpoint

Lesson 9 --- **Relationships Without Database Foreign Keys** is
complete.

The core concepts established are:

``` text
relationship()          → maps object relationships, not DB columns
Mapped[list["X"]]       → collection relationship
Mapped["X"]             → scalar relationship
primaryjoin             → explicit join SQLAlchemy cannot infer
foreign(...)            → identifies the referencing side
back_populates          → connects/synchronises both directions
association model       → relationship represented by a real ORM object
string target           → avoids direct imports; class must be registered
app/models/__init__.py  → central model-registration point
configure_mappers()     → force mapper configuration / sanity check
```

Relationships implemented and verified during the lesson include:

``` text
Product 1 ───── * ProductVariant

Collection 1 ───── * CollectionArtwork * ───── 1 Artwork

Artwork 1 ───── * ArtworkImage * ───── 1 Image
```

Equivalent association relationships can now follow the same pattern
without spending separate learning lessons on identical mechanics.

The polymorphic Product target:

``` text
productable_type + productable_id
```

is genuinely different and remains a later design concern rather than
being forced into the ordinary relationship pattern.

The next lesson is:

``` text
Lesson 10
Querying with SQLAlchemy
```

------------------------------------------------------------------------

# Quick Memory Refresh

``` text
alembic revision -m ...  → create migration/revision
revision                 → current revision ID
down_revision            → immediate parent revision
upgrade()                → move schema forward
downgrade()              → reverse revision
op                       → Alembic operations interface
sa                       → SQLAlchemy alias

alembic upgrade head     → migrate to latest revision
alembic downgrade -1     → move back one revision
alembic upgrade head --sql
                         → generate SQL without applying
alembic current          → current database revision
alembic history          → full revision chain
alembic_version          → current position, not full history

DeclarativeBase          → common base/metadata for ORM models
Mapped[T]                → SQLAlchemy mapped Python attribute
mapped_column(...)       → map attribute to database column
relationship(...)        → map object-to-object relationship

Mapped[list["X"]]        → collection relationship / uselist=True
Mapped["X"]              → scalar relationship / uselist=False
primaryjoin              → explicit ORM join condition
foreign(...)             → mark referencing side of explicit join
back_populates           → connect/synchronise relationship directions

__table__                → SQL/table metadata
__mapper__               → ORM mapper metadata
__mapper__.relationships → mapped ORM relationships

association model        → explicit model for relationship with own data
app.models import        → central model registration
Base.registry            → declarative mapped-class registry
configure_mappers()      → force mapper configuration / sanity check

DB foreign keys          → deliberately not used
cross-table integrity    → application responsibility
ORM relationships        → supported through explicit joins

productable_type + id    → polymorphic Product target
price_amount             → VARCHAR/String by design
```

Current checkpoint:

``` text
Lesson 7 — First SQLAlchemy ORM Model                    ✓
Lesson 8 — Remaining Core Models                         ✓
Lesson 9 — Relationships Without Database Foreign Keys   ✓
Lesson 10 — Querying with SQLAlchemy                      ✓
Lesson 11 — Writing Data and Unit of Work                  NEXT
```

------------------------------------------------------------------------

# 99. Lesson 10: Querying with SQLAlchemy

Lesson 10 introduced the SQLAlchemy 2.x ORM querying workflow against
the real JamesDoe V6 PostgreSQL database.

The fundamental pattern is:

``` python
from sqlalchemy import select

statement = select(Collection)
collections = session.scalars(statement).all()
```

The important separation is:

``` text
select(...)
    → build a SQLAlchemy Select object
    → no database access yet

Session execution
    → execute the statement against PostgreSQL
    → obtain results
```

For example:

``` python
statement = select(Collection)
```

produces a `sqlalchemy.sql.selectable.Select` object. Printing it shows
the SQLAlchemy-generated SQL, with the mapped columns listed explicitly
rather than using `SELECT *`.

------------------------------------------------------------------------

# 100. `execute()`, Result Rows, and `scalars()`

A statement can be executed through the Session:

``` python
result = session.execute(statement)
```

The flow is:

``` text
Select object
    ↓
Session.execute(...)
    ↓
Engine
    ↓
Psycopg
    ↓
PostgreSQL
    ↓
Result
```

`execute()` is a general-purpose API and works in terms of result rows.
When selecting one ORM entity:

``` python
select(Collection)
```

a result row conceptually contains one selected value:

``` text
(Collection(...),)
```

`scalars()` extracts that selected value from each result row:

``` python
result = session.execute(statement)
collections = result.scalars().all()
```

SQLAlchemy also provides the convenient ORM-oriented form:

``` python
collections = session.scalars(statement).all()
```

A useful mental model is:

``` text
execute(...)      → result rows
scalars()         → selected value from each row
all()             → collect all values into a Python list
```

Here, "scalar" does not mean only a primitive value such as an integer
or string. A `Collection` ORM object can be the scalar value because it
is the single selected thing in each result row.

------------------------------------------------------------------------

# 101. Lists, Tuples, and List Comprehensions

Lesson 10 also introduced a few Python collection concepts while
inspecting query results.

A list uses square brackets and is mutable:

``` python
item = [1, "Coffee & Sketch"]
item[1] = "Archive"
```

A tuple normally uses parentheses and is immutable:

``` python
item = (1, "Coffee & Sketch")
```

A useful starting mental model is:

``` text
list  []  → mutable collection of things
tuple ()  → fixed grouping of things
```

PHP arrays do not have this exact distinction.

We also used a list comprehension:

``` python
result = [
    (collection.id, collection.title)
    for collection in collections
]
```

which is a compact form of:

``` python
result = []

for collection in collections:
    result.append((collection.id, collection.title))
```

The outer value is a list; each `(id, title)` value is a tuple.

------------------------------------------------------------------------

# 102. Filtering with `where()` and Bound Parameters

SQLAlchemy filtering uses `where()`:

``` python
statement = select(Collection).where(
    Collection.slug == "coffee-and-sketch"
)
```

This produces SQL resembling:

``` sql
WHERE collections.slug = :slug_1
```

`Collection.slug == "coffee-and-sketch"` does not immediately evaluate
to a Python boolean. `Collection.slug` is a SQLAlchemy mapped attribute,
so the comparison constructs a SQL expression.

`:slug_1` is a bound parameter. SQLAlchemy passes the value separately
to the database driver rather than manually interpolating it into the
SQL string.

Multiple conditions passed to `where()` are combined with `AND`:

``` python
statement = select(Collection).where(
    Collection.slug == "coffee-and-sketch",
    Collection.is_visible.is_(True),
)
```

Chaining `where()` calls is equivalent:

``` python
statement = (
    select(Collection)
    .where(Collection.slug == "coffee-and-sketch")
    .where(Collection.is_visible.is_(True))
)
```

For boolean SQL expressions we used:

``` python
Collection.is_visible.is_(True)
Collection.is_visible.is_(False)
```

------------------------------------------------------------------------

# 103. Retrieving Many, One, or No Results

SQLAlchemy provides different result methods depending on the
cardinality the application expects.

``` text
Method          0 rows       1 row         2+ rows

.all()          []           [obj]         [obj, obj...]
.first()        None         obj           first obj
.one_or_none()  None         obj           MultipleResultsFound
.one()          NoResultFound obj          MultipleResultsFound
```

For example:

``` python
collection = session.scalars(statement).one_or_none()
```

means that zero or one result is valid, but multiple results violate the
query's expected cardinality.

For a unique field such as `Collection.slug`, `one_or_none()` clearly
expresses that expectation.

We deliberately called:

``` python
session.scalars(statement).one()
```

against an empty table and observed:

``` text
sqlalchemy.exc.NoResultFound:
No row was found when one was required
```

------------------------------------------------------------------------

# 104. Ordering and Limiting

Ordering uses `order_by()`:

``` python
statement = (
    select(Collection)
    .where(Collection.is_visible.is_(True))
    .order_by(Collection.sort_order)
)
```

Descending order uses:

``` python
.order_by(Collection.sort_order.desc())
```

Limiting uses:

``` python
.limit(10)
```

For example:

``` python
statement = (
    select(Collection)
    .where(Collection.is_visible.is_(True))
    .order_by(Collection.sort_order)
    .limit(10)
)
```

A useful naming convention is to distinguish the unexecuted statement
from the executed result:

``` python
statement = select(Collection)
collections = session.scalars(statement).all()
```

After `.all()`, `collections` is a Python `list`; it is no longer a
SQLAlchemy statement.

------------------------------------------------------------------------

# 105. Creating Query Data During Lesson 10

The database was initially empty, so we created two real `Collection`
rows to make the query exercises meaningful:

``` python
from uuid import uuid4

coffee_and_sketch = Collection(
    uuid=uuid4(),
    title="Coffee & Sketch",
    slug="coffee-and-sketch",
    description="Coffee & Sketch publications and artwork.",
    is_visible=True,
    sort_order=10,
)

archive = Collection(
    uuid=uuid4(),
    title="Archive",
    slug="archive",
    description="Archived artwork.",
    is_visible=False,
    sort_order=20,
)
```

Before persistence:

``` text
coffee_and_sketch.id → None
archive.id           → None
```

We temporarily borrowed two write operations from Lesson 11:

``` python
session.add(coffee_and_sketch)
session.add(archive)
session.commit()
```

After the commit, PostgreSQL-generated values were available on the same
ORM objects:

``` text
coffee_and_sketch.id → 1
archive.id           → 2
```

The `created_at` values were also populated from the PostgreSQL
`server_default=func.now()` definition.

The mechanics of `add()`, flushing, committing, generated values, and
the Unit of Work are intentionally deferred to Lesson 11.

------------------------------------------------------------------------

# 106. ORM Objects Returned from Real Queries

With persisted data, this query:

``` python
collections = session.scalars(
    select(Collection)
    .where(Collection.is_visible.is_(True))
    .order_by(Collection.sort_order)
).all()
```

returned a Python list containing a real mapped object:

``` text
list[Collection]
```

Attributes can then be accessed normally:

``` python
collections[0].id
collections[0].title
collections[0].slug
```

The complete path is:

``` text
PostgreSQL row
    ↓
Psycopg
    ↓
SQLAlchemy
    ↓
Collection ORM object
    ↓
normal Python attributes
```

------------------------------------------------------------------------

# 107. Primary-Key Lookup and the Session Identity Map

For a primary-key lookup, SQLAlchemy provides:

``` python
collection = session.get(Collection, 1)
```

This is roughly comparable to:

``` php
Collection::find(1);
```

If the primary key does not exist, `Session.get()` returns `None`.

We then observed:

``` python
collection1 = session.get(Collection, 1)
collection2 = session.get(Collection, 1)

collection1 is collection2
# True

collection1 is coffee_and_sketch
# True
```

Python's `is` asks whether two references point to the exact same Python
object in memory.

The SQLAlchemy Session maintains an **identity map**. Conceptually:

``` text
(Collection, 1) → one Collection Python object
(Collection, 2) → one Collection Python object
```

Within one Session, one database identity corresponds to one Python
object identity. This becomes particularly important when modifying
tracked objects in Lesson 11.

------------------------------------------------------------------------

# 108. `IN` and `OR` Conditions

SQL `IN` is represented with `in_()`:

``` python
collections = session.scalars(
    select(Collection)
    .where(Collection.id.in_([1, 2]))
    .order_by(Collection.id)
).all()
```

For explicit `OR` expressions, SQLAlchemy provides `or_()`:

``` python
from sqlalchemy import or_

statement = select(Collection).where(
    or_(
        Collection.slug == "coffee-and-sketch",
        Collection.slug == "archive",
    )
)
```

For several possible values of the same column, `in_()` is normally
cleaner:

``` python
Collection.slug.in_(["coffee-and-sketch", "archive"])
```

`or_()` is useful when the alternatives are different conditions, for
example:

``` python
or_(
    Collection.is_visible.is_(True),
    Collection.sort_order > 15,
)
```

------------------------------------------------------------------------

# 109. `LIKE` and `ILIKE`

SQL text matching is exposed directly by mapped string attributes.

Case-sensitive SQL `LIKE`:

``` python
Collection.title.like("%Sketch%")
```

PostgreSQL case-insensitive `ILIKE`:

``` python
Collection.title.ilike("%sketch%")
```

For example:

``` python
collections = session.scalars(
    select(Collection).where(
        Collection.title.ilike("%sketch%")
    )
).all()
```

matches `Coffee & Sketch` even though the search text uses lowercase.

------------------------------------------------------------------------

# 110. Pagination with `limit()` and `offset()`

Basic offset pagination uses:

``` python
.limit(per_page)
.offset((page - 1) * per_page)
```

For example:

``` python
page = 2
per_page = 10

statement = (
    select(Collection)
    .order_by(Collection.id)
    .limit(per_page)
    .offset((page - 1) * per_page)
)
```

The offset calculation is:

``` text
offset = (page - 1) * per_page

page 1, 10/page → offset 0
page 2, 10/page → offset 10
page 3, 10/page → offset 20
```

Pagination should use a deterministic `ORDER BY`. SQL does not guarantee
row order without one, so paginating an unordered query can produce
unstable results.

------------------------------------------------------------------------

# 111. Counting and `Session.scalar()`

Counting introduced SQLAlchemy's SQL function namespace:

``` python
from sqlalchemy import func

statement = select(func.count()).select_from(Collection)
```

which represents:

``` sql
SELECT count(*)
FROM collections
```

Because this query returns one row containing one selected value, we
used the singular Session method:

``` python
count = session.scalar(statement)
```

With the two lesson records:

``` text
all collections     → 2
visible collections → 1
```

A filtered count is:

``` python
visible_count = session.scalar(
    select(func.count())
    .select_from(Collection)
    .where(Collection.is_visible.is_(True))
)
```

Useful distinction:

``` text
session.scalars(...) → potentially many selected scalar values
session.scalar(...)  → one scalar value
```

------------------------------------------------------------------------

# 112. Lesson 10 Checkpoint

Lesson 10 --- **Querying with SQLAlchemy** is complete.

The core query patterns established are:

``` text
select(Model)             → build an ORM SELECT statement
Session.execute(...)      → execute and obtain result rows
Session.scalars(...)      → execute and expose selected scalar values
.all()                    → all results as a list
.first()                  → first result or None
.one_or_none()            → zero or one; error if multiple
.one()                    → exactly one; error otherwise
Session.get(Model, id)    → primary-key lookup
.where(...)               → filtering
or_(...)                  → OR conditions
.in_(...)                 → SQL IN
.like(...) / .ilike(...)  → text matching
.order_by(...)            → deterministic ordering
.limit(...)               → limit result count
.offset(...)              → offset/pagination
func.count()              → SQL COUNT
Session.scalar(...)       → one scalar result
```

The lesson also established the Session identity map:

``` text
one database identity
        ↓
one Python ORM object per Session
```

and reinforced several Python concepts encountered naturally during
querying:

``` text
list                  → mutable sequence
 tuple                 → immutable/fixed sequence
list comprehension    → compact construction of a list from an iterable
is                    → object identity comparison
```

The next lesson is:

``` text
Lesson 11
Writing Data and Unit of Work
```

------------------------------------------------------------------------

# 113. Lesson 11: Writing Data and Unit of Work

Lesson 11 introduced SQLAlchemy's write lifecycle and the **Unit of
Work** model. Rather than treating each model write as an isolated
operation, a `Session` tracks the objects and changes that belong to the
current unit of database work.

The core lifecycle encountered during the lesson was:

``` text
TRANSIENT
    │
    │ session.add()
    ▼
PENDING
    │
    │ flush / INSERT
    ▼
PERSISTENT
```

SQLAlchemy object state can be inspected with:

``` python
from sqlalchemy import inspect

state = inspect(obj)

state.transient
state.pending
state.persistent
state.deleted
```

------------------------------------------------------------------------

# 114. Transient ORM Objects

Constructing an ORM object creates an ordinary Python object but does
not persist anything:

``` python
new_collection = Collection(
    uuid=uuid4(),
    title="Motorcycles",
    slug="motorcycles",
    description="Motorcycle artwork.",
    is_visible=True,
    sort_order=30,
)
```

At this point:

``` text
transient   → True
pending     → False
persistent  → False
id          → None
```

`transient` means the ORM object exists in Python but is not currently
part of a SQLAlchemy Session and has not been persisted.

------------------------------------------------------------------------

# 115. `Session.add()` and Pending State

Calling:

``` python
session.add(new_collection)
```

registers the object with the Session's Unit of Work.

Its state becomes:

``` text
transient   → False
pending     → True
persistent  → False
```

`Session.add()` does not necessarily issue an `INSERT` immediately. It
tells the Session that the object should be persisted when the Unit of
Work is flushed.

Pending objects can also be observed through:

``` python
new_collection in session.new
```

The useful mental model is:

``` text
Session
├── new objects
├── modified objects
└── objects scheduled for deletion
```

------------------------------------------------------------------------

# 116. `flush()` vs `commit()`

Calling:

``` python
session.flush()
```

synchronises the Session's current Unit of Work with PostgreSQL **inside
the current transaction**.

For a pending object this means an `INSERT` is issued. After the flush:

``` text
pending     → False
persistent  → True
```

Database-generated values such as the identity primary key become
available:

``` python
new_collection.id
```

The important distinction is:

``` text
flush()
    → send pending INSERT / UPDATE / DELETE work to PostgreSQL
    → remain inside the current transaction

commit()
    → flush pending work if necessary
    → COMMIT the transaction
    → make the transaction permanent
```

Therefore:

``` text
flush() ≠ commit()
```

A flushed change can still be rolled back.

------------------------------------------------------------------------

# 117. Rollback After a Flushed INSERT

After flushing a new object, calling:

``` python
session.rollback()
```

reverses the database transaction. The inserted row does not remain in
PostgreSQL.

A newly inserted object that is rolled back returns to a transient
state. Values that were populated onto the Python object during the
flush, such as a generated identity value, may still remain on the
ordinary Python attribute.

This reinforces an important distinction:

``` text
Python object state ≠ committed database state
```

PostgreSQL identity/sequence values are not intended to be gapless. An
identity value consumed by an insert that is later rolled back can
therefore leave a gap.

------------------------------------------------------------------------

# 118. `commit()` Automatically Flushes

A normal insert can be written as:

``` python
session.add(new_collection)
session.commit()
```

An explicit `flush()` is not required before `commit()` because commit
flushes pending changes first.

Conceptually:

``` text
session.commit()
      │
      ├── flush
      │     ↓
      │   INSERT / UPDATE / DELETE
      │
      └── COMMIT
            ↓
      transaction permanent
```

During the lesson the successfully committed `Motorcycles` collection
received ID `4` and could subsequently be queried from PostgreSQL.

------------------------------------------------------------------------

# 119. Failed Flushes and `PendingRollbackError`

The lesson encountered a useful real failure when the object was
accidentally constructed with:

``` python
uuid=uuid4
```

instead of:

``` python
uuid=uuid4()
```

The first form stores the **function itself**. The second calls the
function and stores the returned UUID.

Psycopg therefore rejected the first value:

``` text
cannot adapt type 'function'
```

Because `session.commit()` automatically flushes, the error happened
during the commit's flush phase.

After a flush/commit failure, the Session's transaction is in a failed
state. Before the Session can be used again, call:

``` python
session.rollback()
```

Otherwise SQLAlchemy raises `PendingRollbackError`.

The practical rule is:

> If a SQLAlchemy flush or commit fails, roll back the Session before
> trying to continue using it.

------------------------------------------------------------------------

# 120. Dirty Tracking for Updates

Persistent ORM objects are tracked by their Session. Updating a mapped
attribute is therefore enough to make the object dirty:

``` python
motorcycles.description = "Motorcycles, cafe racers and rider artwork."
```

The Session can report this:

``` python
session.is_modified(motorcycles)
# True

motorcycles in session.dirty
# True
```

There is no Eloquent-style requirement to call a model-level `save()`
method. The Session's Unit of Work detects the mapped attribute change
and issues the required `UPDATE` when it flushes.

A rough comparison is:

``` text
Eloquent
    object.attribute = value
    object.save()

SQLAlchemy
    object.attribute = value
    Session tracks the change
    Session flushes/commits the Unit of Work
```

------------------------------------------------------------------------

# 121. Attribute Change History

SQLAlchemy can expose pending attribute history:

``` python
state = inspect(motorcycles)
state.attrs.description.history
```

Before a flush, a fully loaded previous value can produce history such
as:

``` text
History(
    added=['Motorcycles, cafe racers and rider artwork.'],
    unchanged=(),
    deleted=['Motorcycle and cafe-racer artwork.']
)
```

Here `deleted` means the old attribute value was replaced. It does not
mean the row or column was deleted.

After `flush()` the new value becomes the Session's synchronised
transaction state:

``` text
History(
    added=(),
    unchanged=['Motorcycles, cafe racers and rider artwork.'],
    deleted=()
)
```

Attribute history describes the ORM's current change state; it is not a
permanent audit log.

We also observed that after a commit SQLAlchemy may expire attributes by
default. If the previous value has not been loaded again before
replacement, that old value may not appear in `history.deleted`.

------------------------------------------------------------------------

# 122. Rollback After a Flushed UPDATE

The update lifecycle observed was:

``` text
modify mapped attribute
        ↓
object becomes DIRTY
        ↓
flush()
        ↓
UPDATE sent to PostgreSQL
        ↓
object no longer dirty
        ↓
transaction still open
        ↓
rollback()
        ↓
UPDATE reversed
```

After rollback, reading the attribute returned the previously committed
value:

``` text
'Motorcycle and cafe-racer artwork.'
```

This demonstrates that `flush()` synchronises with the **current
transaction**; it does not make the update permanent.

------------------------------------------------------------------------

# 123. Deleting ORM Objects

A persistent object can be scheduled for deletion with:

``` python
session.delete(motorcycles)
```

Before flushing:

``` python
motorcycles in session.deleted
# True
```

but inspection showed:

``` text
state.persistent → True
state.deleted    → False
```

This means the object is still persistent but is scheduled for deletion
by the Unit of Work.

After:

``` python
session.flush()
```

we observed:

``` text
motorcycles in session.deleted → False
state.persistent               → False
state.deleted                  → True
```

The distinction is:

``` text
Before flush
    session.deleted → objects waiting for DELETE
    state.deleted   → False

After flush
    DELETE has been issued
    session.deleted → False
    state.deleted   → True
```

------------------------------------------------------------------------

# 124. Rollback After a Flushed DELETE

Because the DELETE had only been flushed, it could still be reversed:

``` python
session.rollback()
```

The `Motorcycles` collection remained queryable afterward.

The query returned the same Python ORM object:

``` python
motorcycles_again is motorcycles
# True
```

This connects Lesson 11 back to Lesson 10's Session identity map:

``` text
(Collection, 4)
      ↓
same Python object within the Session
```

Rollback restored the object's persistent database state without
creating a replacement ORM instance.

------------------------------------------------------------------------

# 125. The SQLAlchemy Unit of Work

The Session can coordinate several kinds of change together:

``` python
session.add(new_collection)

motorcycles.title = "Motorcycle Art"

session.delete(archive)
```

Conceptually the Session now tracks:

``` text
Session
│
├── NEW
│   └── new_collection
│
├── DIRTY
│   └── motorcycles
│
└── DELETED
    └── archive
```

A flush synchronises the complete Unit of Work:

``` text
INSERT new_collection
UPDATE motorcycles
DELETE archive
```

within the same database transaction.

The transaction can then be resolved with either:

``` text
commit()
    → make the transaction permanent

rollback()
    → discard the transaction
```

This is the central Lesson 11 mental model: the SQLAlchemy Session
coordinates object identity, change tracking, persistence operations,
and the current Unit of Work.

------------------------------------------------------------------------

# 126. Session Lifetime in FastAPI Requests

JamesDoe V6 already uses the request-scoped dependency:

``` python
def get_db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
```

The lifecycle is:

``` text
HTTP request
    ↓
get_db()
    ↓
SessionLocal()
    ↓
yield Session
    ↓
endpoint/application work
    ↓
get_db() resumes
    ↓
finally
    ↓
session.close()
```

This implements the locked architecture decision:

> One SQLAlchemy Session per HTTP request.

A single request can therefore perform several related database
operations as one coherent Unit of Work.

For example:

``` text
create Artwork
create Image
create ArtworkImage
create Product
create ProductVariant
        ↓
one transaction
        ↓
commit all or rollback all
```

------------------------------------------------------------------------

# 127. `close()` Is Not `commit()`

Session lifetime and transaction outcome are separate responsibilities.

``` python
session.close()
```

means that the application has finished using that Session and its
resources should be cleaned up/released.

It does **not** mean:

``` text
save whatever happened during this request
```

The important separation is:

``` text
commit()    → make current transaction permanent
rollback()  → discard current transaction
close()     → finish using/clean up the Session
```

------------------------------------------------------------------------

# 128. Transaction Boundary Decision for JamesDoe V6

Two broad patterns were considered.

A request dependency could automatically commit or roll back around
every request, or application/service code could explicitly control the
transaction.

For now, JamesDoe V6 keeps `get_db()` responsible only for Session
lifetime:

``` python
def get_db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
```

Transaction decisions remain explicit in the application/service
operation. Conceptually:

``` text
get_db()
    → how long does this Session live?

application/service operation
    → should this Unit of Work commit or rollback?
```

This keeps transaction behaviour visible while the application layer is
still being developed. A more abstract transaction boundary can be
introduced later if real application code justifies it.

------------------------------------------------------------------------

# 129. Lesson 11 Checkpoint

Lesson 11 --- **Writing Data and Unit of Work** is complete.

The core concepts established are:

``` text
transient                 → Python ORM object not attached to a Session
pending                   → added to Session; awaiting INSERT
persistent                → ORM object represents persistent Session state
dirty                     → persistent object has pending mapped changes
deleted                   → DELETE has been flushed for the object

Session.add(...)          → register a new object with the Unit of Work
Session.delete(...)       → schedule persistent object for deletion
Session.flush()           → synchronise pending SQL inside current transaction
Session.commit()          → flush if necessary, then commit transaction
Session.rollback()        → reverse current transaction
Session.close()           → finish using/clean up Session resources

session.new               → pending new objects
session.dirty             → tracked modified objects
session.deleted           → objects scheduled for deletion
session.is_modified(...)  → ask whether mapped state has changed
inspect(obj)              → inspect ORM object state and attribute history
```

The complete write lifecycle can be summarised as:

``` text
INSERT
transient
    ↓ add()
pending
    ↓ flush()
persistent

UPDATE
persistent
    ↓ attribute assignment
dirty
    ↓ flush()
persistent / synchronised

DELETE
persistent
    ↓ delete()
scheduled for deletion
    ↓ flush()
deleted
```

And the transaction boundary is:

``` text
Unit of Work
    ↓
flush()
    ↓
SQL synchronised inside transaction
    ↓
┌───────────────┬────────────────┐
│ commit()      │ rollback()     │
│ permanent     │ discard        │
└───────────────┴────────────────┘
```

Current checkpoint:

``` text
Lesson 7  — First SQLAlchemy ORM Model                    ✓
Lesson 8  — Remaining Core Models                         ✓
Lesson 9  — Relationships Without Database Foreign Keys   ✓
Lesson 10 — Querying with SQLAlchemy                      ✓
Lesson 11 — Writing Data and Unit of Work                 ✓
Lesson 12 — Relationship Loading and N+1                  ✓
```

------------------------------------------------------------------------

# 130. Lesson 12 --- Relationship Loading and the N+1 Problem

SQLAlchemy relationships describe how ORM objects are connected, but defining a
relationship does not mean that the related rows are always fetched with the
parent object.

For example, `Product.variants` can exist as an ORM relationship while the
`ProductVariant` rows remain unloaded until the attribute is accessed.

The important distinction is therefore:

``` text
relationship configured
        ≠
relationship data already loaded
```

------------------------------------------------------------------------

# 131. Lazy Relationship Loading

The default relationship behaviour we observed is **lazy loading**.

A query such as:

``` python
product = session.scalars(
    select(Product).where(Product.id == 1)
).one()
```

loads the `Product`, but does not necessarily load `product.variants`.

Conceptually:

``` text
SELECT product
    ↓
Product object created
    ↓
variants relationship still unloaded
    ↓
product.variants accessed
    ↓
SQLAlchemy issues another SELECT
```

Lazy loading is convenient because related data is only fetched when it is
actually needed. The trade-off is that attribute access can cause database I/O
that is not obvious from the Python expression itself.

A useful Laravel comparison is accessing an Eloquent relationship without
eager-loading it first.

------------------------------------------------------------------------

# 132. The N+1 Query Problem

Lazy loading becomes particularly important when querying multiple parent
objects.

For example:

``` python
products = session.scalars(select(Product)).all()

for product in products:
    print(product.variants)
```

If the variants relationship is lazy-loaded, the database work can become:

``` text
1 query   → load all Products
N queries → load variants separately for each Product

Total = 1 + N queries
```

For ten products this can mean eleven queries. For one hundred products it can
mean one hundred and one queries.

This is the **N+1 query problem**.

The problem is not the relationship itself. The problem is repeatedly
lazy-loading the relationship while iterating over a collection of parent
objects.

------------------------------------------------------------------------

# 133. Eager Loading with `selectinload()`

When we know in advance that related rows will be needed, SQLAlchemy can load
them eagerly.

For collection relationships such as `Product.variants`, we used:

``` python
from sqlalchemy.orm import selectinload

product = session.scalars(
    select(Product)
    .options(selectinload(Product.variants))
    .where(Product.id == 1)
).one()
```

`selectinload()` tells SQLAlchemy that the relationship should be populated as
part of executing this query rather than waiting for later attribute access.

Conceptually, for multiple products:

``` text
Query 1
SELECT products ...

Query 2
SELECT product_variants ...
WHERE product_id IN (...)
```

So instead of:

``` text
1 + N queries
```

we can often get:

``` text
2 queries
```

for the parent collection and its related collection.

The exact SQL is SQLAlchemy's responsibility; the important application-level
decision is that the relationship is deliberately requested up front.

------------------------------------------------------------------------

# 134. `selectinload()` Does Not Mean SQL JOIN

The word **eager** describes *when* related data is loaded, not necessarily *how*
it is loaded.

`selectinload()` normally uses a separate SELECT for the related rows. It does
not combine the parent and child rows into one large result set.

Conceptually:

``` text
selectinload()

SELECT parents
        +
SELECT children WHERE parent_id IN (...)
```

This is useful for one-to-many and many-to-many collection relationships
because it avoids repeating parent rows in a joined result while still avoiding
the N+1 pattern.

------------------------------------------------------------------------

# 135. `joinedload()`

SQLAlchemy also provides `joinedload()`.

Conceptually:

``` python
from sqlalchemy.orm import joinedload

select(Product).options(joinedload(Product.variants))
```

This asks SQLAlchemy to load the relationship using a JOIN as part of the query.

The rough distinction is:

``` text
selectinload()  → parent SELECT + related SELECT using IN (...)
joinedload()    → parent and related rows loaded through a JOIN
```

Neither strategy is universally better. The appropriate loader depends on the
relationship shape and query. For JamesDoe V6, `selectinload()` is a strong
default for collection relationships when we know the collection will be
needed.

------------------------------------------------------------------------

# 136. Session Lifetime and Lazy Loading

Lazy loading requires an active ORM context capable of going back to the
database. This became clear in our detached-object experiment.

We first loaded a product without eager-loading its variants:

``` python
session = SessionLocal()

product = session.scalars(
    select(Product).where(Product.id == 1)
).one()

session.close()
```

At that point the `Product` object still existed as a normal Python object, but
it was detached from the Session.

Trying to access an unloaded relationship:

``` python
product.variants
```

produced `DetachedInstanceError`.

The reason was not that detached ORM objects cease to exist. The problem was
that `variants` had not been loaded, and SQLAlchemy would have needed the Session
to perform the lazy-loading query.

Conceptually:

``` text
Product loaded
    ↓
variants UNLOADED
    ↓
Session closed
    ↓
Product becomes detached
    ↓
product.variants
    ↓
needs database query
    ↓
no active Session available
    ↓
DetachedInstanceError
```

------------------------------------------------------------------------

# 137. Eager Loading Before Detaching

We then repeated the experiment using `selectinload()`:

``` python
session = SessionLocal()

product = session.scalars(
    select(Product)
    .options(selectinload(Product.variants))
    .where(Product.id == 1)
).one()

session.close()
```

After closing the Session:

``` python
product.variants
```

still worked, and:

``` python
[(v.id, v.title) for v in product.variants]
```

returned:

``` text
[(2, 'A2 Print'), (1, 'A3 Print')]
```

This proves that the relationship objects had already been materialised before
the Session was closed.

Conceptually:

``` text
Product loaded
    +
selectinload(Product.variants)
    ↓
Product + variants LOADED
    ↓
Session closed
    ↓
objects detached
    ↓
product.variants
    ↓
already present in memory
    ↓
works without another query
```

The important qualification is that this does **not** make a detached ORM object
capable of loading arbitrary additional data. Only state that was already
loaded remains directly available. Accessing some other unloaded relationship
after the Session has closed can still require database access and therefore
fail.

------------------------------------------------------------------------

# 138. Relationship Loading Is a Query Decision

A useful architectural lesson from this is that relationship loading should be
driven by the use case.

For example:

``` text
GET /products
    → perhaps product summary data only
    → variants may not be needed

GET /products/{id}
    → product detail response includes variants
    → load variants deliberately
```

We therefore do not need to configure every relationship to be eagerly loaded
globally. Query-specific loader options allow the application to request the
data required by a particular operation.

This keeps database behaviour explicit and avoids both unnecessary loading and
accidental N+1 queries.

------------------------------------------------------------------------

# 139. Laravel / SQLAlchemy Mental Mapping

The rough conceptual mapping is:

``` text
Laravel / Eloquent                 SQLAlchemy
---------------------------------  -----------------------------------
relationship method/property       relationship()
lazy relationship access           lazy relationship loading
with('variants')                    selectinload(Product.variants)
eager loading                       eager loading
N+1 problem                         N+1 problem
model outside useful ORM context    detached ORM object
```

The APIs differ, but the performance problem and the reason for eager loading
are fundamentally the same.

------------------------------------------------------------------------

# 140. Lesson 12 Checkpoint

Lesson 12 --- **Relationship Loading and the N+1 Problem** is complete.

The core concepts established are:

``` text
relationship configured           ≠ relationship data loaded

lazy loading                      → load relationship when accessed
eager loading                     → deliberately load relationship up front
selectinload(...)                  → eager load using additional SELECT(s)
joinedload(...)                    → eager load through a JOIN
N+1                               → one parent query + repeated relationship queries

open Session + unloaded relation  → lazy loading can query database
closed Session + unloaded relation
                                  → DetachedInstanceError when loading is required
closed Session + loaded relation  → already-loaded objects remain usable
```

The practical rule for JamesDoe V6 is:

``` text
Do not eager-load every relationship automatically.

Load relationships deliberately when the application operation needs them,
and watch collection queries for accidental N+1 behaviour.
```

Current checkpoint:

``` text
Lesson 7  — First SQLAlchemy ORM Model                    ✓
Lesson 8  — Remaining Core Models                         ✓
Lesson 9  — Relationships Without Database Foreign Keys   ✓
Lesson 10 — Querying with SQLAlchemy                      ✓
Lesson 11 — Writing Data and Unit of Work                 ✓
Lesson 12 — Relationship Loading and N+1                  ✓
```

------------------------------------------------------------------------
