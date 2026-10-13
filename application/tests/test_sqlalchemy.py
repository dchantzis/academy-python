from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from academy_examples.models import Product, seeded_session

def test_seeded_database_is_isolated():
    with seeded_session() as session:
        assert len(session.scalars(select(Product)).all()) == 2

def test_selectinload_variants():
    with seeded_session() as session:
        products = session.scalars(select(Product).options(selectinload(Product.variants))).all()
        assert sorted(len(p.variants) for p in products) == [2, 2]

def test_joinedload_unique():
    with seeded_session() as session:
        products = session.scalars(select(Product).options(joinedload(Product.variants))).unique().all()
        assert len(products) == 2

def test_flush_and_rollback():
    with seeded_session() as session:
        session.add(Product(name="temporary"))
        session.flush()
        session.rollback()
        assert session.scalar(select(Product).where(Product.name == "temporary")) is None
