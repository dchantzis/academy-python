# Lesson 13 — Pydantic API Models

**Accelerated mode:** ~20–25 minutes. **Goal:** Understand Pydantic validation and API request/response schemas.

## Key ideas

- **SQLAlchemy** maps Python objects to database rows (similar to Laravel Eloquent).
- **Pydantic** validates and serializes data (similar to Laravel Form Requests and API Resources).
- Unlike TypeScript interfaces, Pydantic performs **runtime** validation.
- Request schemas describe accepted input; response schemas describe exposed output. Neither needs to mirror every database column.

## Example

```python
from pydantic import BaseModel, Field

class ArtworkCreate(BaseModel):
    title: str
    price: float = Field(ge=0)

class ArtworkResponse(ArtworkCreate):
    id: int
```

`Field(ge=0)` rejects negative values. `model_dump()` returns a Python `dict`; `model_dump_json()` returns a JSON `str`.

## SQLAlchemy integration

```python
from pydantic import BaseModel, ConfigDict

class ArtworkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str

# Given a SQLAlchemy model instance `db_artwork`:
# response = ArtworkResponse.model_validate(db_artwork)
```

`from_attributes=True` allows Pydantic to read object attributes rather than requiring a dictionary.

## FastAPI integration (illustrative)

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class ArtworkCreate(BaseModel):
    title: str
    price: float = Field(ge=0)

class ArtworkResponse(ArtworkCreate):
    id: int

@app.post('/artworks', response_model=ArtworkResponse, status_code=201)
def create_artwork(data: ArtworkCreate):
    # No persistence yet: demonstration only.
    return {'id': 42, **data.model_dump()}
```

FastAPI validates incoming request data, validates and serializes the response, and returns HTTP **422** for invalid request bodies.

## Run

From the `academy-python` repository root (with Pydantic v2 installed):

```bash
python application/lessons/13_pydantic_api_models/main.py
```

The runnable `main.py` demonstrates validation, serialization and attribute-based conversion; it does not start a server.

## Quick knowledge check

1. Does Pydantic replace SQLAlchemy? **No:** persistence versus validation/serialization.
2. `model_dump()` versus `model_dump_json()`? **Python dict versus JSON string.**
3. Why separate creation and response schemas? **Input and output have different requirements.**

**Scope:** Educational examples only; no JamesDoe V6 entities or database changes.
