# Lesson 14 — FastAPI Routing, Dependencies & Database Sessions

**Accelerated mode · 20–30 minutes**

## Goals

- Define typed HTTP routes using FastAPI decorators and `APIRouter`.
- Inject dependencies with `Depends()` and `Annotated`.
- Understand per-request SQLAlchemy sessions and `yield`-based cleanup.
- Explore FastAPI's **automatic OpenAPI documentation**, Swagger UI, and ReDoc.

## Laravel ↔ FastAPI

| Laravel | FastAPI |
| --- | --- |
| `Route::get('/artworks/{id}', ...)` | `@router.get('/{artwork_id}')` |
| Controller method | Endpoint function |
| Container injection | `Depends(provider)` |
| `Artwork::find($id)` | `db.get(Artwork, id)` |
| `abort(404)` | `raise HTTPException(status_code=404, ...)` |
| API docs via tools such as Scribe / Scramble / L5-Swagger | OpenAPI and interactive docs built in |

## 1. Routing and parameter validation

```python
@router.get('/{artwork_id}')
def get_artwork(artwork_id: int):
    return {'id': artwork_id}
```

`GET /artworks/42` matches and parses the path parameter as an integer. `GET /artworks/abc` returns **HTTP 422** because `abc` is not a valid integer.

## 2. Dependency injection

```python
from typing import Annotated
from fastapi import Depends


def get_repository():
    return ArtworkRepository()


def endpoint(repository: Annotated[ArtworkRepository, Depends(get_repository)]):
    ...
```

FastAPI calls the provider and injects the returned value. In the runnable example, `get_artwork_store()` injects an in-memory dictionary instead of a database.

## 3. Database session lifecycle

A typical SQLAlchemy dependency looks like this (illustrative; not wired into this lesson's runnable demo):

```python
from collections.abc import Generator
from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()  # session factory configured elsewhere
    try:
        yield db
    finally:
        db.close()
```

`yield` supplies the session to the endpoint; execution resumes for cleanup afterward. The `finally` block runs even when an exception occurs. **Closing a session does not mean committing changes**: define transaction/commit policy separately.

## 4. APIRouter

```python
router = APIRouter(prefix='/artworks', tags=['artworks'])

@router.get('/{artwork_id}')
def get_artwork(artwork_id: int):
    ...

app.include_router(router)
```

`APIRouter` keeps related endpoints together instead of bloating `main.py`. The `tags` also group endpoints in the generated documentation.

## 5. Automatic API documentation — out of the box

FastAPI generates an **OpenAPI specification** from your declared routes, parameters, Python type annotations, Pydantic schemas, and endpoint metadata. You do **not** need to install a separate Swagger/OpenAPI generator.

Once the server is reachable, open:

| URL | What it provides |
| --- | --- |
| `http://localhost:8000/docs` | **Swagger UI**: interactive documentation; try requests in the browser |
| `http://localhost:8000/redoc` | **ReDoc**: alternative documentation presentation |
| `http://localhost:8000/openapi.json` | Machine-readable **OpenAPI specification** |
| `http://localhost:8000/artworks/42` | Sample artwork JSON |
| `http://localhost:8000/artworks/999` | Sample **404** error |
| `http://localhost:8000/artworks/abc` | Sample **422** parameter-validation error |
| `http://localhost:8000/dependency-demo` | Demonstrates injected dependency and cleanup |
| `http://localhost:8000/` | **404 is expected**: this lesson does not define a root `/` route |

### How FastAPI knows what to document

For example:

```python
from pydantic import BaseModel, Field

class ArtworkCreate(BaseModel):
    title: str
    price: float = Field(ge=0)

class ArtworkResponse(ArtworkCreate):
    id: int

@app.post('/artworks', response_model=ArtworkResponse, status_code=201)
def create_artwork(data: ArtworkCreate):
    ...
```

FastAPI can document the HTTP method and path, required JSON fields, numeric constraint `price >= 0`, response shape, and success status. **This POST route is an illustration, not part of Lesson 14's `main.py`.**

Swagger UI lets you expand an endpoint, choose **Try it out**, enter parameters, and execute a request without Postman. `/openapi.json` describes the same API in a format other tools can consume.

### Why this matters for JamesDoe V6

A possible future workflow is:

```text
Pydantic request/response schemas
            ↓
FastAPI-generated OpenAPI specification
            ↓
TypeScript type/client generation tool
            ↓
React frontend consuming the headless API
```

**Important:** TypeScript generation is *possible* using additional tooling; FastAPI does not generate a TypeScript client by itself. Generated types can reduce duplicated API contracts between Python and TypeScript.

## 6. Run Lesson 14 in academy-python (Docker)

Your Compose configuration mounts the host's `./application` directory at `/var/www` inside the container. Therefore, **do not include `application/` in the path passed to `./dev python`**:

```bash
./dev python lessons/14_fastapi_routing_dependencies/main.py
```

The example requires `fastapi` and `uvicorn` in the project environment. If Uvicorn is missing, add it using your existing uv workflow:

```bash
./dev uv add 'uvicorn[standard]'
```

### Make the server accessible from your browser

Inside `application/lessons/14_fastapi_routing_dependencies/main.py`, the startup code should use:

```python
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
```

`0.0.0.0` here binds **inside the container**. In `docker-compose.yml`, add under the `app` service:

```yaml
ports:
  - '127.0.0.1:8000:8000'
```

This publishes the container's port to **localhost on your development machine only**. Recreate the app container after changing Compose configuration:

```bash
docker compose up -d --force-recreate app
```

Then run the lesson command above in a terminal and visit `http://localhost:8000/docs` on **ares**. Stop the server with `Ctrl+C`.

If the server starts but `/docs` is unreachable, check `docker compose ps` for the `127.0.0.1:8000->8000/tcp` mapping. If `/` returns `{"detail":"Not Found"}` but `/docs` works, the setup is working correctly.

## Knowledge check

1. **What does `Depends(get_db)` do?** Calls the dependency and injects its yielded session.
2. **Why `yield` instead of `return`?** It allows cleanup after the endpoint finishes.
3. **Why `APIRouter`?** To group routes by feature and keep code maintainable.
4. **Where does `/openapi.json` come from?** FastAPI generates it from route declarations, types, schemas and metadata.
5. **Why is `/` a 404?** No route has been registered for the root path.

## Scope

This is an educational example using an in-memory store, **not** the JamesDoe V6 API. Database persistence, migrations, authentication, and production transaction policy are intentionally outside this lesson.
