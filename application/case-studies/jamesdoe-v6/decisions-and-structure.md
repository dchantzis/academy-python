# JamesDoe-specific source topics 23 and 24

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

