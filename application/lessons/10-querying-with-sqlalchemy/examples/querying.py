"""Filtering and ordering with SQLAlchemy 2.x select()."""
from sqlalchemy import select
from academy_examples.models import Product, seeded_session
with seeded_session() as session:
    products = session.scalars(select(Product).where(Product.name.like("Motorcycle%"))
                               .order_by(Product.name)).all()
    print([product.name for product in products])
