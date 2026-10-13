"""Explicit ORM join WITHOUT a database ForeignKey constraint.

This is a teaching contrast, not a general recommendation.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, foreign, mapped_column, relationship
class Base(DeclarativeBase):
    pass
class Parent(Base):
    __tablename__ = "parents"
    id: Mapped[int] = mapped_column(primary_key=True)
    children: Mapped[list["Child"]] = relationship(
        primaryjoin=lambda: Parent.id == foreign(Child.parent_id),
        back_populates="parent",
    )
class Child(Base):
    __tablename__ = "children"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int]
    parent: Mapped[Parent] = relationship(
        primaryjoin=lambda: Parent.id == foreign(Child.parent_id),
        back_populates="children",
    )
if __name__ == "__main__":
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        parent = Parent(children=[Child()])
        session.add(parent)
        session.commit()
        print("parent", parent.id, "children", len(parent.children))
