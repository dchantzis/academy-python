"""flush writes within a transaction; rollback undoes uncommitted writes."""
from sqlalchemy import select
from academy_examples.models import Product, seeded_session
with seeded_session() as session:
    item = Product(name="Temporary product")
    session.add(item)
    print("before flush:", item.id)
    session.flush()
    print("after flush:", item.id)
    session.rollback()
    print("after rollback:", session.scalar(select(Product).where(Product.name == "Temporary product")))
