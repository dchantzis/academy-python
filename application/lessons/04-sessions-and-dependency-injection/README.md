# Lesson 04 — Sessions And Dependency Injection

Migrated from the original Python Backend Foundations learning notes. Original topic numbers are retained; topic order here is grouped by lesson rather than original chronology.

These notes include JamesDoe V6-specific observations from the original learning sessions; see `case-studies/jamesdoe-v6/` for their architectural context.

## Original topic 15: Request-Scoped Sessions

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


## Original topic 35: The Session Factory

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


## Original topic 40: FastAPI `Depends`

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


## Original topic 41: Request-Scoped Session Lifecycle

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


## Original topic 42: Executing SQL and SQLAlchemy Results

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

