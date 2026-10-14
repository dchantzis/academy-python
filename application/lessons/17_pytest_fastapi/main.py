"""Lesson 17: small FastAPI app for testing, with an in-memory repository."""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Academy Python — Lesson 17")


class ArtworkCreate(BaseModel):
    title: str
    price: float = Field(ge=0)


class ArtworkResponse(ArtworkCreate):
    id: int


class ArtworkRepository:
    def __init__(self) -> None:
        self.items: dict[int, ArtworkResponse] = {
            42: ArtworkResponse(id=42, title="Moto Rider", price=150),
        }
        self.next_id = 43

    def find(self, artwork_id: int) -> ArtworkResponse | None:
        return self.items.get(artwork_id)

    def create(self, data: ArtworkCreate) -> ArtworkResponse:
        artwork = ArtworkResponse(id=self.next_id, **data.model_dump())
        self.items[artwork.id] = artwork
        self.next_id += 1
        return artwork


repository = ArtworkRepository()


def get_repository() -> ArtworkRepository:
    return repository


RepositoryDependency = Annotated[ArtworkRepository, Depends(get_repository)]


@app.get("/artworks/{artwork_id}", response_model=ArtworkResponse)
def get_artwork(artwork_id: int, repo: RepositoryDependency) -> ArtworkResponse:
    artwork = repo.find(artwork_id)
    if artwork is None:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return artwork


@app.post("/artworks", response_model=ArtworkResponse, status_code=status.HTTP_201_CREATED)
def create_artwork(data: ArtworkCreate, repo: RepositoryDependency) -> ArtworkResponse:
    return repo.create(data)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
