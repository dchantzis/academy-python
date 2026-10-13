# Lesson 09 — Orm Relationships

Migrated from the original Python Backend Foundations learning notes. Original topic numbers are retained; topic order here is grouped by lesson rather than original chronology.

These notes include JamesDoe V6-specific observations from the original learning sessions; see `case-studies/jamesdoe-v6/` for their architectural context.

## Original topic 86: Lesson 9: ORM Relationships Without Database Foreign Keys

Lesson 9 introduced SQLAlchemy object relationships while preserving the
project's deliberate policy of having no PostgreSQL foreign-key
constraints.

The key distinction is:

``` text
Database foreign key
    → PostgreSQL referential-integrity constraint

SQLAlchemy relationship
    → ORM description of how Python objects relate
```

Because the mapped ID columns do not use `ForeignKey(...)`, SQLAlchemy
cannot infer the join direction automatically. Relationships therefore
use explicit `primaryjoin` expressions together with `foreign()`.

------------------------------------------------------------------------


## Original topic 87: `relationship()` and Relationship Cardinality

SQLAlchemy's `relationship()` maps an object-to-object relationship.

For example, `Product` now has:

``` python
variants: Mapped[list["ProductVariant"]] = relationship(
    "ProductVariant",
    primaryjoin="Product.id == foreign(ProductVariant.product_id)",
    back_populates="product",
)
```

Unlike `mapped_column()`, this does not represent another database
column.

The type annotation expresses cardinality:

``` text
Mapped[list["ProductVariant"]] → collection relationship / one-to-many
Mapped["Product"]              → scalar relationship / many-to-one
```

SQLAlchemy exposes this through `uselist`:

``` python
Product.__mapper__.relationships["variants"].uselist
# True

ProductVariant.__mapper__.relationships["product"].uselist
# False
```

------------------------------------------------------------------------


## Original topic 88: Explicit `primaryjoin` and `foreign()`

With conventional SQLAlchemy `ForeignKey(...)` metadata, SQLAlchemy can
normally infer how mapped tables should be joined. JamesDoe V6
deliberately does not use that metadata.

We therefore state the join explicitly:

``` python
primaryjoin="Product.id == foreign(ProductVariant.product_id)"
```

The underlying relationship is:

``` text
Product.id
    ↑
    │
ProductVariant.product_id
```

`primaryjoin` describes how the rows relate. `foreign()` identifies
`ProductVariant.product_id` as the referencing side.

This is ORM configuration only. It does not create a PostgreSQL
`FOREIGN KEY` constraint.

------------------------------------------------------------------------


## Original topic 89: Bidirectional Relationships and `back_populates`

The Product relationship is configured in both directions.

`Product`:

``` python
variants: Mapped[list["ProductVariant"]] = relationship(
    "ProductVariant",
    primaryjoin="Product.id == foreign(ProductVariant.product_id)",
    back_populates="product",
)
```

`ProductVariant`:

``` python
product: Mapped["Product"] = relationship(
    "Product",
    primaryjoin="foreign(ProductVariant.product_id) == Product.id",
    back_populates="variants",
)
```

`back_populates` names the relationship attribute on the other mapped
class:

``` text
Product.variants
      ↕
ProductVariant.product
```

It also keeps both sides synchronized in Python memory. For example:

``` python
product.variants.append(variant)
```

makes:

``` python
variant.product is product
```

true without separately assigning `variant.product = product`.

------------------------------------------------------------------------


## Original topic 90: ORM Relationship State vs ID Column State

We connected unpersisted objects through the ORM:

``` python
product.variants.append(variant)
```

Before persistence, PostgreSQL has not generated the Product identity
value:

``` text
product.id          → None
variant.product_id  → None
```

Nevertheless:

``` python
variant.product is product
```

is already true.

This demonstrates:

``` text
product.variants / variant.product
    → relationship between Python ORM objects

variant.product_id
    → mapped database column
```

SQLAlchemy can know that two in-memory objects are related before the
database-generated primary key exists. The persistence/flush lifecycle
will be covered later.

------------------------------------------------------------------------


## Original topic 91: Association Models and Relationships

`CollectionArtwork` is an explicit association model rather than an
invisible many-to-many pivot table:

``` text
Collection 1 ───── * CollectionArtwork * ───── 1 Artwork
```

The relationships are:

``` text
Collection.collection_artworks  → list[CollectionArtwork]
CollectionArtwork.collection    → Collection
Artwork.collection_artworks     → list[CollectionArtwork]
CollectionArtwork.artwork       → Artwork
```

For example:

``` python
collection_artworks: Mapped[list["CollectionArtwork"]] = relationship(
    "CollectionArtwork",
    primaryjoin="Collection.id == foreign(CollectionArtwork.collection_id)",
    back_populates="collection",
)
```

with the reverse:

``` python
collection: Mapped["Collection"] = relationship(
    "Collection",
    primaryjoin="foreign(CollectionArtwork.collection_id) == Collection.id",
    back_populates="collection_artworks",
)
```

The association object remains visible because the relationship itself
contains domain data such as `sort_order` and timestamps.

We have not added a direct `collection.artworks` convenience
relationship at this stage.

------------------------------------------------------------------------


## Original topic 92: Artwork Image Association Relationships

`ArtworkImage` follows the same association-model pattern:

``` text
Artwork 1 ───── * ArtworkImage * ───── 1 Image
```

The resulting relationships are:

``` text
Artwork.artwork_images   → list[ArtworkImage]
ArtworkImage.artwork     → Artwork
Image.artwork_images     → list[ArtworkImage]
ArtworkImage.image       → Image
```

The logical joins are:

``` text
Artwork.id = ArtworkImage.artwork_id
Image.id   = ArtworkImage.image_id
```

For example, the Image side is:

``` python
artwork_images: Mapped[list["ArtworkImage"]] = relationship(
    "ArtworkImage",
    primaryjoin="Image.id == foreign(ArtworkImage.image_id)",
    back_populates="image",
)
```

and the reverse is:

``` python
image: Mapped["Image"] = relationship(
    "Image",
    primaryjoin="foreign(ArtworkImage.image_id) == Image.id",
    back_populates="artwork_images",
)
```

The explicit association object is useful because an attachment carries
its own data: `role`, `sort_order`, `is_primary`, and timestamps.

The repeated association pattern is now understood and does not need a
separate learning lesson for every equivalent association table.

------------------------------------------------------------------------


## Original topic 93: String Relationship Targets and the Declarative Registry

Relationship targets are currently referred to by strings:

``` python
relationship("ProductVariant", ...)
relationship("CollectionArtwork", ...)
relationship("ArtworkImage", ...)
```

This helps avoid direct imports between related model modules and the
circular-import problems those imports can create.

However, a string target can only be resolved after its mapped class has
been imported and registered with the common `Base`.

We inspected:

``` python
list(Product.registry._class_registry.keys())
```

Before importing `ProductVariant`, only `Product` and SQLAlchemy's
internal registry entry were present. After importing `ProductVariant`,
that class appeared in the registry.

The important rule is:

``` text
Python file exists
    ≠
mapped class has been registered

module imported
    ↓
class definition executes
    ↓
class inherits Base
    ↓
SQLAlchemy registers mapped class
```

------------------------------------------------------------------------


## Original topic 94: Partial Imports and Mapper Configuration

After adding relationships to `Artwork`, a fresh interpreter imported
`Artwork`, `ArtworkImage`, and `Image`, but not `CollectionArtwork`.

Inspecting `Artwork.__mapper__.relationships` caused mapper
configuration to fail while resolving:

``` python
"Artwork.id == foreign(CollectionArtwork.artwork_id)"
```

because `CollectionArtwork` had not yet been registered.

Importing the complete related model graph allowed mapper configuration
to succeed.

String relationship declarations therefore avoid direct circular
imports, but they do not remove the need for all mapped classes to be
loaded before the complete mapper graph is configured.

------------------------------------------------------------------------


## Original topic 95: Central Model Registration

`app/models/__init__.py` now acts as the central model-registration
point and imports all 11 mapped classes:

``` python
from app.models.artwork import Artwork
from app.models.artwork_image import ArtworkImage
from app.models.collection import Collection
from app.models.collection_artwork import CollectionArtwork
from app.models.image import Image
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.publication import Publication
from app.models.publication_group import PublicationGroup
from app.models.publication_group_publication import PublicationGroupPublication
from app.models.publication_image import PublicationImage
```

Therefore:

``` python
import app.models
```

loads every model module and registers all mapped classes with the
common declarative registry.

These imports have an intentional registration side effect even when the
imported class names are not otherwise referenced by `__init__.py`.

------------------------------------------------------------------------


## Original topic 96: Verifying the Complete Model Registry

After:

``` python
import app.models
from app.database.base import Base
```

we verified:

``` python
list(Base.registry._class_registry.keys())
```

and obtained all 11 application models:

``` text
Artwork
ArtworkImage
Collection
CollectionArtwork
Image
Product
ProductVariant
Publication
PublicationGroup
PublicationGroupPublication
PublicationImage
```

plus SQLAlchemy's internal `_sa_module_registry`.

------------------------------------------------------------------------


## Original topic 97: `configure_mappers()` as a Sanity Check

SQLAlchemy provides:

``` python
from sqlalchemy.orm import configure_mappers

configure_mappers()
```

This forces configuration of the registered mapper graph.

After central model registration, `configure_mappers()` completed
without an exception.

This verifies that SQLAlchemy can resolve and configure the
relationships currently added to the model graph. It is a useful sanity
check after relationship changes because mapper configuration may
otherwise happen lazily.

------------------------------------------------------------------------


## Original topic 98: Lesson 9 Checkpoint

Lesson 9 --- **Relationships Without Database Foreign Keys** is
complete.

The core concepts established are:

``` text
relationship()          → maps object relationships, not DB columns
Mapped[list["X"]]       → collection relationship
Mapped["X"]             → scalar relationship
primaryjoin             → explicit join SQLAlchemy cannot infer
foreign(...)            → identifies the referencing side
back_populates          → connects/synchronises both directions
association model       → relationship represented by a real ORM object
string target           → avoids direct imports; class must be registered
app/models/__init__.py  → central model-registration point
configure_mappers()     → force mapper configuration / sanity check
```

Relationships implemented and verified during the lesson include:

``` text
Product 1 ───── * ProductVariant

Collection 1 ───── * CollectionArtwork * ───── 1 Artwork

Artwork 1 ───── * ArtworkImage * ───── 1 Image
```

Equivalent association relationships can now follow the same pattern
without spending separate learning lessons on identical mechanics.

The polymorphic Product target:

``` text
productable_type + productable_id
```

is genuinely different and remains a later design concern rather than
being forced into the ordinary relationship pattern.

The next lesson is:

``` text
Lesson 10
Querying with SQLAlchemy
```

------------------------------------------------------------------------

# Quick Memory Refresh

``` text
alembic revision -m ...  → create migration/revision
revision                 → current revision ID
down_revision            → immediate parent revision
upgrade()                → move schema forward
downgrade()              → reverse revision
op                       → Alembic operations interface
sa                       → SQLAlchemy alias

alembic upgrade head     → migrate to latest revision
alembic downgrade -1     → move back one revision
alembic upgrade head --sql
                         → generate SQL without applying
alembic current          → current database revision
alembic history          → full revision chain
alembic_version          → current position, not full history

DeclarativeBase          → common base/metadata for ORM models
Mapped[T]                → SQLAlchemy mapped Python attribute
mapped_column(...)       → map attribute to database column
relationship(...)        → map object-to-object relationship

Mapped[list["X"]]        → collection relationship / uselist=True
Mapped["X"]              → scalar relationship / uselist=False
primaryjoin              → explicit ORM join condition
foreign(...)             → mark referencing side of explicit join
back_populates           → connect/synchronise relationship directions

__table__                → SQL/table metadata
__mapper__               → ORM mapper metadata
__mapper__.relationships → mapped ORM relationships

association model        → explicit model for relationship with own data
app.models import        → central model registration
Base.registry            → declarative mapped-class registry
configure_mappers()      → force mapper configuration / sanity check

DB foreign keys          → deliberately not used
cross-table integrity    → application responsibility
ORM relationships        → supported through explicit joins

productable_type + id    → polymorphic Product target
price_amount             → VARCHAR/String by design
```

Current checkpoint:

``` text
Lesson 7 — First SQLAlchemy ORM Model                    ✓
Lesson 8 — Remaining Core Models                         ✓
Lesson 9 — Relationships Without Database Foreign Keys   ✓
Lesson 10 — Querying with SQLAlchemy                      ✓
Lesson 11 — Writing Data and Unit of Work                  NEXT
```

------------------------------------------------------------------------

