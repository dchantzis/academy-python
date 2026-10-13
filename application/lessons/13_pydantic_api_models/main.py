"""Lesson 13: Pydantic API models; standalone, no database or web server."""
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class ArtworkCreate(BaseModel):
    title: str
    price: float = Field(ge=0)


class ArtworkResponse(ArtworkCreate):
    id: int


class ArtworkFromAttributes(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str


def main() -> None:
    incoming = ArtworkCreate(title="Moto Rider", price=150)
    outgoing = ArtworkResponse(id=42, **incoming.model_dump())
    print("Request:", incoming.model_dump())
    print("Response dict:", outgoing.model_dump())
    print("Response JSON:", outgoing.model_dump_json())

    try:
        ArtworkCreate(title="Invalid", price=-50)
    except ValidationError as exc:
        print("Validation error:", exc.errors()[0]["msg"])

    class DatabaseLikeArtwork:
        id = 42
        title = "Moto Rider"

    print("From attributes:", ArtworkFromAttributes.model_validate(DatabaseLikeArtwork()).model_dump())


if __name__ == "__main__":
    main()
