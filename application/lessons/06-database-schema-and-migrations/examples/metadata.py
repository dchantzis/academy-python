"""SQLAlchemy schema constraints, independent of Alembic migration scripts."""
from sqlalchemy import Column, Integer, MetaData, String, Table, UniqueConstraint
metadata = MetaData()
collections = Table(
    "collections", metadata,
    Column("id", Integer, primary_key=True),
    Column("slug", String(100), nullable=False),
    UniqueConstraint("slug", name="uq_collections_slug"),
)
if __name__ == "__main__":
    print(collections.name, [c.name for c in collections.columns])
