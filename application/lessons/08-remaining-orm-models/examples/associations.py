"""Inspect association entities in a small independent training model."""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
class Base(DeclarativeBase):
    pass
class CollectionArtwork(Base):
    __tablename__ = "collection_artwork"
    id: Mapped[int] = mapped_column(primary_key=True)
    collection_id: Mapped[int]
    artwork_id: Mapped[int]
    sort_order: Mapped[int]
if __name__ == "__main__":
    print(CollectionArtwork.__table__)
