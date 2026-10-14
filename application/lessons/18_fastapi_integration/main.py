"""Lesson 18: end-to-end FastAPI feature (ephemeral SQLite demo)."""

from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class Artwork(Base):
    __tablename__ = "artworks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    internal_note: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ArtworkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str


# SQLite is used only to keep this educational example self-contained.
# StaticPool shares one in-memory database across sessions and threads.
engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


router = APIRouter(prefix="/artworks", tags=["artworks"])


@router.get(
    "/{artwork_id}",
    response_model=ArtworkResponse,
    responses={404: {"description": "Artwork not found"}},
)
def get_artwork(
    artwork_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Artwork:
    artwork = db.get(Artwork, artwork_id)
    if artwork is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artwork not found",
        )
    return artwork


app = FastAPI(title="Academy Python — Lesson 18", version="1.0.0")
app.include_router(router, prefix="/api/v1")


def setup_demo_database() -> None:
    """Create and seed an ephemeral demo DB; not a production migration."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.get(Artwork, 42) is None:
            db.add(
                Artwork(
                    id=42,
                    title="Moto Rider",
                    slug="moto-rider",
                    internal_note="Not exposed through the API",
                )
            )
            db.commit()


if __name__ == "__main__":
    import uvicorn

    setup_demo_database()
    uvicorn.run(app, host="0.0.0.0", port=8000)
