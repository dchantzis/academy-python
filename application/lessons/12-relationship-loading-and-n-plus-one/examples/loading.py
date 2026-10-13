"""Compare lazy, selectinload and joinedload; note joinedload requires unique()."""
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from academy_examples.models import Product, seeded_session
with seeded_session() as session:
    lazy = session.scalars(select(Product)).all()
    print("lazy:", [(p.name, len(p.variants)) for p in lazy])
with seeded_session() as session:
    eager = session.scalars(select(Product).options(selectinload(Product.variants))).all()
    print("selectinload:", [(p.name, len(p.variants)) for p in eager])
with seeded_session() as session:
    joined = session.scalars(select(Product).options(joinedload(Product.variants))).unique().all()
    print("joinedload:", [(p.name, len(p.variants)) for p in joined])
