# Lesson 15 — FastAPI Error Handling & HTTP Responses

**Accelerated lesson:** ~15–20 minutes.  
**Goal:** Understand automatic validation, HTTP exceptions, custom domain exceptions, and OpenAPI error documentation.

## Laravel ↔ FastAPI

| Laravel | FastAPI |
| --- | --- |
| `throw` / `abort(404)` | `raise HTTPException(status_code=404, ...)` |
| Form Request validation | Pydantic request model; FastAPI returns 422 for invalid requests |
| Custom exception and renderer | Custom `Exception` and `@app.exception_handler(...)` |
| `response()->json(..., 201)` | `status_code=201` on route or `JSONResponse` |
| API docs via additional tooling | OpenAPI automatically at `/docs`, `/redoc`, `/openapi.json` |

## Core concepts

### 1. Explicit HTTP errors

```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Artwork not found",
)
```

Python uses `raise` where PHP uses `throw`. `HTTPException` is appropriate at the HTTP boundary.

### 2. Automatic validation errors (422)

```python
from pydantic import BaseModel, Field

class ArtworkCreate(BaseModel):
    title: str
    slug: str
    price: float = Field(ge=0)
```

An incoming negative `price` fails request validation, and FastAPI returns HTTP 422 before the endpoint function runs. `ge=0` allows zero; use `gt=0` for strictly positive values.

### 3. Business conflicts (409)

A valid request may conflict with existing state, e.g. a duplicate artwork slug. We explicitly raise `HTTPException(status_code=409, ...)`. In a real database-backed API, enforce uniqueness with a **database unique constraint** as well: checking first does not prevent concurrent inserts.

### 4. Domain exceptions and registered handlers

```python
class ArtworkNotFoundError(Exception):
    def __init__(self, artwork_id: int):
        self.artwork_id = artwork_id

@app.exception_handler(ArtworkNotFoundError)
async def artwork_not_found_handler(request: Request, exc: ArtworkNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "ARTWORK_NOT_FOUND",
            "message": f"Artwork {exc.artwork_id} not found",
        },
    )
```

`@app.exception_handler(ArtworkNotFoundError)` **registers** the handler; it does not call it immediately. When an `ArtworkNotFoundError` propagates during request processing, FastAPI/Starlette invokes the registered handler and uses its response.

Request flow:

```text
GET /artworks/999
  → endpoint looks up artwork
  → raises ArtworkNotFoundError(999)
  → framework invokes artwork_not_found_handler(request, exc)
  → HTTP 404 JSON response
```

This lets service/domain code express errors without depending on HTTP-specific exceptions. If code catches and handles the exception earlier, it will not reach this handler.

### 5. Documenting errors in OpenAPI

```python
@app.get(
    "/artworks/{artwork_id}",
    responses={404: {"description": "Artwork not found"}},
)
```

`responses={...}` **documents** a response; it does **not** implement the error-handling logic. Inspect the generated documentation at `/docs`.

## Run the example

The repository's `application/` directory is mounted at `/var/www` inside Docker, so omit `application/` from the path passed to `./dev python`:

```bash
./dev python lessons/15_fastapi_error_handling/main.py
```

Open **http://localhost:8000/docs**. This requires the app container to publish port `8000` (e.g. `127.0.0.1:8000:8000` in `docker-compose.yml`), and the example binds Uvicorn to `0.0.0.0` inside the container. Stop Lesson 14's server first to avoid a port conflict.

Try:

1. `GET /artworks/42` → **200**, existing artwork.
2. `GET /artworks/999` → **404**, handled by `artwork_not_found_handler()`.
3. `POST /artworks` with `{"title":"Another","slug":"another","price":-5}` → **422**, automatic Pydantic validation.
4. `POST /artworks` with `{"title":"Duplicate","slug":"moto-rider","price":10}` → **409**, explicit business conflict.
5. `POST /artworks` with `{"title":"New work","slug":"new-work","price":10}` → **201**, new artwork.

**Note:** This is a learning example using an in-memory dictionary, not SQLAlchemy or PostgreSQL. Changes disappear when the server restarts, and it is not designed for concurrent writes.

## Knowledge check

1. **422 vs 409?** 422: invalid request data; 409: valid data conflicting with current state.
2. **Why domain exceptions?** Keep domain/service logic independent of HTTP and centralize consistent responses.
3. **Does `responses={404: ...}` implement 404 behavior?** No, it documents it.
