# Lesson 08 — Remaining Orm Models

Migrated from the original Python Backend Foundations learning notes. Original topic numbers are retained; topic order here is grouped by lesson rather than original chronology.

These notes include JamesDoe V6-specific observations from the original learning sessions; see `case-studies/jamesdoe-v6/` for their architectural context.

## Original topic 72: Association Models

Several many-to-many relationships use explicit association tables,
including:

``` text
collection_artwork
publication_group_publication
```

Rather than treating them as invisible pivot tables, we map them as ORM
classes because they contain their own data, including `sort_order` and
timestamps.

For example:

``` python
class CollectionArtwork(Base):
    __tablename__ = "collection_artwork"

    collection_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    artwork_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
```

A rough Laravel comparison is an explicit pivot model rather than only
using an implicit `belongsToMany` pivot table.

------------------------------------------------------------------------


## Original topic 73: ORM `UniqueConstraint`

Composite uniqueness is represented at model level using
`UniqueConstraint`.

For example:

``` python
__table_args__ = (
    UniqueConstraint("collection_id", "artwork_id"),
)
```

This means the **pair** must be unique.

It does not mean each column must individually be unique.

``` text
collection_id   artwork_id

1               10    ✓
1               11    ✓
2               10    ✓
1               10    ✗ duplicate pair
```

This also reinforced a Python tuple rule:

``` python
(value,)
```

is a one-element tuple.

Parentheses alone do not create a tuple; the trailing comma does.

Other mapped composite unique constraints include:

``` text
images
    → disk + path

artwork_image
    → artwork_id + image_id + role

publication_image
    → publication_id + image_id + role

publication_group_publication
    → publication_group_id + publication_id
```

------------------------------------------------------------------------


## Original topic 74: ORM `CheckConstraint`

`Publication` maps the database rule:

``` sql
CHECK (volume > 0)
```

using:

``` python
__table_args__ = (
    CheckConstraint("volume > 0"),
)
```

Because `volume` itself is nullable:

``` text
NULL        → allowed
1, 2, 3... → allowed
0, -1...   → rejected by the database
```

This is an example of a local row invariant that remains useful to
enforce at database level even though cross-table referential integrity
is application-owned.

------------------------------------------------------------------------


## Original topic 75: Application-Level Enum-Like Strings in ORM Models

Columns such as:

``` text
artwork_image.role
publication_image.role
publications.publication_type
products.productable_type
products.product_type
product_variants.status
```

remain ordinary SQLAlchemy `String(...)` columns.

For example:

``` python
status: Mapped[str] = mapped_column(
    String(50),
    nullable=False,
    server_default="active",
)
```

Expected values can be documented in code:

``` python
# draft | active | sold | out_of_stock | archived
```

but SQLAlchemy/PostgreSQL are not currently modelling these as database
enum types.

Validation remains an application responsibility and will become more
explicit as the Pydantic/application layers are built.

------------------------------------------------------------------------


## Original topic 76: Image Attachment Models and Roles

Artwork and publication images use explicit attachment models:

``` text
ArtworkImage
PublicationImage
```

Each records:

``` text
parent entity ID
image ID
role
sort_order
is_primary
timestamps
```

For `ArtworkImage`, the unique combination is:

``` text
artwork_id + image_id + role
```

This deliberately allows the same image to be attached to the same
artwork under different roles.

The same pattern applies to publication images.

The scalar attachment IDs are now complemented by explicit ORM
relationships for `ArtworkImage`. Equivalent attachment relationships
can follow the same pattern.

------------------------------------------------------------------------


## Original topic 77: Explicit and Composite ORM Indexes

A simple single-column index can be declared on a mapped column using:

``` python
index=True
```

For example:

``` python
artwork_id: Mapped[int] = mapped_column(
    BigInteger,
    nullable=False,
    index=True,
)
```

SQLAlchemy will generate an index name automatically in its metadata.

When an existing migration has an important explicit name, or when the
index spans multiple columns, we can instead use `Index(...)`.

For example, `Product` has:

``` python
__table_args__ = (
    Index(
        "products_productable_idx",
        "productable_type",
        "productable_id",
    ),
)
```

This maps the existing database index:

``` sql
CREATE INDEX products_productable_idx
ON products (productable_type, productable_id);
```

A useful distinction:

``` text
index=True
    → convenient single-column index

Index("name", "a", "b")
    → explicit named index; can span multiple columns
```

Using explicit names also helps keep ORM metadata aligned with the names
already created by migrations.

------------------------------------------------------------------------


## Original topic 78: Polymorphic Product References

`Product` introduced an important domain pattern:

``` text
productable_type
productable_id
```

For example:

``` text
productable_type = "artwork"
productable_id   = 72
```

means:

``` text
artworks.id = 72
```

while:

``` text
productable_type = "publication"
productable_id   = 72
```

means:

``` text
publications.id = 72
```

Therefore `productable_id` has no complete meaning by itself.

The logical reference is the pair:

``` text
(productable_type, productable_id)
```

The same numeric ID can legitimately exist in both target tables.

This is also why a conventional database foreign key cannot directly
describe this polymorphic reference: the target table depends on the
value of `productable_type`.

Existence and type correctness are therefore application-layer
responsibilities.

------------------------------------------------------------------------


## Original topic 79: Why the Product Polymorphic Index Is Composite

Products are indexed by:

``` text
productable_type + productable_id
```

rather than only by `productable_id`.

The ORM declaration is:

``` python
Index(
    "products_productable_idx",
    "productable_type",
    "productable_id",
)
```

This reflects how the reference is actually interpreted.

Conceptually, queries are interested in combinations such as:

``` text
"artwork", 72
"publication", 72
```

rather than the ambiguous value `72` alone.

------------------------------------------------------------------------


## Original topic 80: `ProductVariant` and Exact Monetary Strings

`ProductVariant` preserves the locked monetary design:

``` python
price_amount: Mapped[str] = mapped_column(
    String(50),
    nullable=False,
)
```

It is deliberately **not** mapped as:

``` text
float
Decimal
Numeric
```

because the database stores the exact external representation as a
string.

The ORM model should faithfully map the canonical database schema rather
than silently redesign it.

If calculations are required later, application code can parse the
string into an exact numeric representation such as `Decimal`.

------------------------------------------------------------------------


## Original topic 81: Product Variant Stock and Status Semantics

Important `ProductVariant` fields include:

``` text
quantity
    → nullable integer for depletable physical stock

is_unlimited
    → boolean indicating non-depleting/unlimited stock

status
    → application-controlled lifecycle value

is_default
    → identifies the default variant for a product
```

Expected status values are:

``` text
draft
active
sold
out_of_stock
archived
```

`quantity` may be `NULL` when stock quantity is not applicable, such as
an unlimited digital product.

These semantics belong to the application/domain layer; the ORM model
maps the underlying columns.

------------------------------------------------------------------------


## Original topic 82: Multiple Explicit Indexes on `ProductVariant`

`ProductVariant` maps three existing indexes:

``` python
__table_args__ = (
    Index(
        "product_variants_product_idx",
        "product_id",
    ),
    Index(
        "product_variants_default_idx",
        "product_id",
        "is_default",
    ),
    Index(
        "product_variants_status_idx",
        "status",
    ),
)
```

These correspond to:

``` text
product_variants_product_idx
    → product_id

product_variants_default_idx
    → product_id + is_default

product_variants_status_idx
    → status
```

Even the single-column indexes are expressed explicitly here so their
ORM metadata names match the already-existing migration names.

------------------------------------------------------------------------


## Original topic 83: Completed Core ORM Models

The complete core-domain model set is now:

``` text
Collection
Artwork
CollectionArtwork
Image
ArtworkImage
Publication
PublicationImage
PublicationGroup
PublicationGroupPublication
Product
ProductVariant
```

That is:

``` text
11 core database tables
        ↕
11 SQLAlchemy ORM models
```

The models now describe columns, types, nullability, defaults,
constraints, and indexes.

The model set now also includes the first object-to-object
relationships; relationship configuration is documented in Lesson 9
below.

------------------------------------------------------------------------


## Original topic 84: ORM Models Do Not Require Database Foreign Keys

The project still deliberately has no PostgreSQL foreign-key
constraints.

That does not prevent us from using SQLAlchemy ORM relationships.

The important distinction is:

``` text
Database foreign key
    → PostgreSQL enforces cross-table referential integrity

ORM relationship
    → SQLAlchemy understands how Python objects relate
```

Because our columns do not contain `ForeignKey(...)` metadata,
SQLAlchemy cannot automatically infer all of the joins.

We therefore configure relevant joins explicitly with `relationship()`,
`primaryjoin`, and `foreign()`.

For example, SQLAlchemy currently sees:

``` text
ProductVariant.product_id
```

as a `BIGINT` value.

Lesson 9 now configures object access such as:

``` python
product.variants
variant.product
```

without introducing PostgreSQL foreign-key constraints.

------------------------------------------------------------------------


## Original topic 85: Current ORM Inspection Workflow

The smoke-test workflow used while creating models is:

``` python
from app.models.product_variant import ProductVariant

ProductVariant.__table__.columns.keys()
ProductVariant.__table__.c.keys()
ProductVariant.__mapper__.attrs.keys()
ProductVariant.__table__.indexes
```

These checks answer different questions:

``` text
columns.keys()
    → what columns does SQLAlchemy think the table has?

c.keys()
    → shorthand for the same columns collection

__mapper__.attrs.keys()
    → what attributes are mapped by the ORM?

__table__.indexes
    → what indexes are represented in model metadata?
```

This provided a quick way to compare each ORM model against the already
applied migration/schema.

------------------------------------------------------------------------

