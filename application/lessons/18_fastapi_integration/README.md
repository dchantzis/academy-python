# Lesson 18 — Putting Everything Together

**Accelerated course · Final lesson**

## Goal

Connect FastAPI routing, dependency injection, SQLAlchemy, Pydantic, HTTP errors, Alembic, and pytest into one small, understandable feature. This example uses an **in-memory SQLite database** so it runs without the optional PostgreSQL container. JamesDoe V6 should use its existing PostgreSQL architecture, not copy this database choice.

## Architecture

```text
GET /api/v1/artworks/{artwork_id}
  → FastAPI router
  → Depends(get_db): SQLAlchemy Session
  → Artwork ORM model / database query
  → ArtworkResponse (Pydantic)
  → HTTP JSON response (or HTTP 404)
```

| Python / FastAPI | PHP / Laravel analogy |
| --- | --- |
| SQLAlchemy mapped model | Eloquent model |
| Pydantic response schema | API Resource |
| `APIRouter` | Routes + controller grouping |
| `Depends(get_db)` | Dependency injection / request-scoped DB work |
| `HTTPException(404)` | `abort(404)` |
| pytest + `TestClient` | PHPUnit/Pest HTTP tests |
| Alembic revisions | Laravel migrations |

## Files

- `main.py` — self-contained runnable API with an SQLAlchemy model, Pydantic response schema, dependency, and router.
- `test_main.py` — tests for 200, 404, 422, and response field filtering; tests override `get_db` and do not touch the demo database.

## Run

From the `academy-python` repository root:

```bash
./dev python lessons/18_fastapi_integration/main.py
```

Then open <http://localhost:8000/docs> or <http://localhost:8000/redoc>. This assumes your existing Docker configuration publishes `127.0.0.1:8000:8000`, as configured in Lesson 14, and Uvicorn is installed.

The example seeds a single artwork into **SQLite memory** on startup. Nothing is persisted when the server stops.

Run the tests separately (no server or PostgreSQL required):

```bash
./dev python -m pytest lessons/18_fastapi_integration/test_main.py -v
```

Dependencies: `fastapi`, `sqlalchemy`, `pydantic`, `uvicorn`, `pytest`, and `httpx` (the last two for testing). Install missing packages using the repo's existing `uv` workflow.

## How the pieces connect

1. `Artwork` is an SQLAlchemy ORM class mapping the `artworks` table.
2. `ArtworkResponse` is the API contract; `from_attributes=True` allows Pydantic to read ORM attributes.
3. `get_db()` yields a session and closes it after use.
4. `APIRouter` groups endpoints under `/artworks` and the app adds `/api/v1`.
5. `response_model=ArtworkResponse` filters and serializes output.
6. `HTTPException(status_code=404)` handles missing records; FastAPI returns 422 for invalid integer path parameters.
7. Tests override `get_db` with a fake session to avoid touching the demonstration database.

## Where Alembic fits

Alembic manages **schema evolution**, outside the HTTP request lifecycle. In this standalone educational example, `Base.metadata.create_all()` is used only to set up an ephemeral demo database. **Do not use `create_all()` as a replacement for reviewed Alembic migrations in JamesDoe V6.**

Typical Alembic workflow in a real project:

```bash
alembic revision --autogenerate -m "describe change"
# Review generated migration carefully, especially renames and data changes.
alembic upgrade head
alembic current
```

## Important limitations

- This is an educational read-only API, not production architecture.
- It does not implement authentication, pagination, logging, or production-grade error responses.
- Its SQLite demo does not test PostgreSQL-specific behaviour.
- The fake-session tests exercise HTTP contracts, **not** real SQLAlchemy queries or constraints. Use a dedicated PostgreSQL test database for integration tests.
- Before Codex implements JamesDoe V6, inspect the actual repository and its locked schema decisions. Do not automatically expose CRUD endpoints for every table.

## Knowledge check (answers)

1. **Why ORM and response schemas?** ORM maps persisted data; Pydantic defines the public API contract.
2. **Who decides response fields?** `response_model=ArtworkResponse` and its declared fields.
3. **When do migrations run?** As deliberate schema-management/deployment operations, not on each HTTP request.
4. **Why override the database in tests?** To isolate test execution from real application data; separately test database behaviour with an isolated PostgreSQL instance.
