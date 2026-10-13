# JamesDoe V6 — learning case study

This material describes **project-specific** implementation choices made during Lessons 1–12. It is not a dependency of academy-python and does not imply that these conventions are universal best practices.

- Python + FastAPI + synchronous SQLAlchemy 2 + Psycopg 3 + PostgreSQL 17.
- One SQLAlchemy Session per HTTP request; cleanup dependency closes the Session.
- Explicit application/service-level commit and rollback; dependency does not auto-commit.
- Database foreign keys deliberately omitted; ORM relationships use explicit `primaryjoin` and `foreign()`.
- Core domain schema: collections, artworks, collection_artwork, images, artwork_image, publications, publication_image, publication_groups, publication_group_publication, products, product_variants.
- Relationship loading experiments covered N+1, `selectinload`, `joinedload`, `.unique()`, and detached lazy loading.

See `decisions-and-structure.md` for the verbatim original source topics 23 and 24. For complete original context see `archive/original-documents/`.
