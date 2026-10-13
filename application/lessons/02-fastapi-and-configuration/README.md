# Lesson 02 — Fastapi And Configuration

Migrated from the original Python Backend Foundations learning notes. Original topic numbers are retained; topic order here is grouped by lesson rather than original chronology.

These notes include JamesDoe V6-specific observations from the original learning sessions; see `case-studies/jamesdoe-v6/` for their architectural context.

## Original topic 2: FastAPI

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


## Original topic 3: The FastAPI Application Object

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


## Original topic 7: Application Settings

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


## Original topic 8: `SettingsConfigDict`

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


## Original topic 9: Debug Mode

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


## Original topic 16: FastAPI Dependency Injection

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


## Original topic 17: Synchronous vs Asynchronous Code

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


## Original topic 18: Why PHP Concurrency Felt Different

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


## Original topic 19: Synchronous FastAPI Still Handles Concurrent Requests

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


## Original topic 20: Concurrency Is Not Rate Limiting

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


## Original topic 21: Kubernetes Is Another Scaling Layer

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

