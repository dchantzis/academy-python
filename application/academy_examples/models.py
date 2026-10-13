"""Independent teaching schema. SQLite in memory; no production database."""
from sqlalchemy import ForeignKey, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    variants: Mapped[list["ProductVariant"]] = relationship(back_populates="product")

class ProductVariant(Base):
    __tablename__ = "product_variants"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    label: Mapped[str] = mapped_column(String(100))
    price_minor: Mapped[int] = mapped_column(Integer)
    product: Mapped[Product] = relationship(back_populates="variants")

def seeded_session() -> Session:
    """Return a Session with a fresh database and two sample products."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add_all([
        Product(name="Motorcycle Art Print", variants=[
            ProductVariant(label="A3", price_minor=2500),
            ProductVariant(label="A2", price_minor=4000),
        ]),
        Product(name="Motorcycle Art Postcard", variants=[
            ProductVariant(label="Single", price_minor=300),
            ProductVariant(label="Pack of 5", price_minor=1200),
        ]),
    ])
    session.commit()
    return session
