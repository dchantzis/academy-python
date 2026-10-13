"""Lesson 14: runnable FastAPI routing and dependency injection demo."""

from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from pydantic import BaseModel


class ArtworkResponse(BaseModel):
    id: int
    title: str


ARTWORKS = {42: ArtworkResponse(id=42, title="Moto Rider")}


def get_artwork_store() -> dict[int, ArtworkResponse]:
    """An injected in-memory store; a real API would use a DB session."""
    return ARTWORKS


def request_resource() -> Generator[str, None, None]:
    """Demonstrate yield-based cleanup without requiring a database."""
    print("Dependency: acquire resource")
    try:
        yield "ready"
    finally:
        print("Dependency: release resource")


router = APIRouter(prefix="/artworks", tags=["artworks"])


@router.get("/{artwork_id}", response_model=ArtworkResponse)
def get_artwork(
    artwork_id: int,
    store: Annotated[dict[int, ArtworkResponse], Depends(get_artwork_store)],
) -> ArtworkResponse:
    artwork = store.get(artwork_id)
    if artwork is None:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return artwork


app = FastAPI(title="Academy Python — Lesson 14")
app.include_router(router)


@app.get("/dependency-demo")
def dependency_demo(resource: Annotated[str, Depends(request_resource)]) -> dict[str, str]:
    return {"resource": resource}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
