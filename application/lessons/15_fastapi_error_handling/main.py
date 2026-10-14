"""Lesson 15: FastAPI HTTP errors and custom exception handlers.

Run inside academy-python: ./dev python lessons/15_fastapi_error_handling/main.py
"""
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Academy Python — Lesson 15")


class ArtworkCreate(BaseModel):
    title: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    price: float = Field(ge=0)


class ArtworkResponse(ArtworkCreate):
    id: int


class ArtworkNotFoundError(Exception):
    def __init__(self, artwork_id: int):
        self.artwork_id = artwork_id


@app.exception_handler(ArtworkNotFoundError)
async def artwork_not_found_handler(request: Request, exc: ArtworkNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "ARTWORK_NOT_FOUND",
            "message": f"Artwork {exc.artwork_id} not found",
        },
    )


artworks: dict[int, ArtworkResponse] = {
    42: ArtworkResponse(id=42, title="Moto Rider", slug="moto-rider", price=150.0)
}


@app.get(
    "/artworks/{artwork_id}",
    response_model=ArtworkResponse,
    responses={404: {"description": "Artwork not found"}},
)
def get_artwork(artwork_id: int):
    artwork = artworks.get(artwork_id)
    if artwork is None:
        raise ArtworkNotFoundError(artwork_id)
    return artwork


@app.post(
    "/artworks",
    response_model=ArtworkResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Artwork slug already exists"}},
)
def create_artwork(data: ArtworkCreate):
    if any(existing.slug == data.slug for existing in artworks.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Artwork slug already exists",
        )
    artwork_id = max(artworks, default=0) + 1
    artwork = ArtworkResponse(id=artwork_id, **data.model_dump())
    artworks[artwork_id] = artwork
    return artwork


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
