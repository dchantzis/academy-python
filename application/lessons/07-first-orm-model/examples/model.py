"""Declarative SQLAlchemy model inspection."""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
class Base(DeclarativeBase):
    pass
class Collection(Base):
    __tablename__ = "collections"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str]
if __name__ == "__main__":
    print(Collection.__table__)
