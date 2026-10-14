# Lesson 17 — Testing FastAPI with pytest

**Accelerated lesson · 20–30 minutes**

## Objectives

- Use `pytest` and Python's built-in `assert`.
- Test FastAPI routes with `TestClient` (no Uvicorn server required).
- Understand fixtures and parametrized tests.
- Distinguish mocked dependencies from a real, isolated test database.

## Laravel ↔ Python

| Laravel / PHP | Python / FastAPI |
| --- | --- |
| PHPUnit / Pest | pytest |
| HTTP feature test | `TestClient` |
| `setUp()` / reusable test setup | `@pytest.fixture` |
| Data provider | `@pytest.mark.parametrize` |
| Container binding override | `app.dependency_overrides` |

## Run

From the `academy-python` repository root:

```bash
./dev python -m pytest lessons/17_pytest_fastapi/test_main.py -v
```

The lesson needs `pytest`, `fastapi`, `httpx`, and `pydantic` in the project environment. If `httpx` is missing, add it as a development dependency using your existing `uv` workflow (`./dev uv add --dev httpx`). Similarly, add `pytest` if necessary.

The tests do **not** start Uvicorn or need a Docker port mapping. `TestClient` calls the ASGI application in-process.

## Example architecture

- `main.py` defines a small FastAPI app, Pydantic request schema, and in-memory artwork repository.
- `test_main.py` demonstrates fixtures, success/404/422 responses, parametrization, and dependency overrides.
- The example deliberately has **no SQLAlchemy/PostgreSQL connection**. In a real application, override `get_db` to use an isolated test database, not production/staging.

## Key concepts

### Fixture injection

```python
@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_something(client):
    ...
```

pytest matches the `client` parameter to the fixture name and injects its value. `yield` supports cleanup afterward.

### Dependency override

```python
app.dependency_overrides[get_repository] = lambda: test_repository
# ... run tests ...
app.dependency_overrides.clear()
```

Overrides replace FastAPI dependency providers during a test. This does **not** automatically mean mocking: the replacement may be an in-memory fake or a real test database session.

### Validation

`Field(ge=0)` permits **zero** and rejects negative prices. Invalid request bodies return HTTP **422** before the endpoint executes.

## Knowledge check (with answers)

1. **Why no Uvicorn?** `TestClient` invokes the ASGI application directly.
2. **How are fixtures selected?** pytest injects fixtures requested by name in test parameters.
3. **Why override DB dependencies?** To isolate tests from production/staging data; optionally use a separate real PostgreSQL database for integration tests.

## JamesDoe V6 note

For the actual API, prefer tests against an isolated PostgreSQL test database for SQLAlchemy relationships, transactions, and database constraints. Keep the application database untouched.
