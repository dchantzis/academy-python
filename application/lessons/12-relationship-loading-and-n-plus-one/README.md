# Lesson 12 — Relationship Loading And N Plus One

Migrated from the original Python Backend Foundations learning notes. Original topic numbers are retained; topic order here is grouped by lesson rather than original chronology.

These notes include JamesDoe V6-specific observations from the original learning sessions; see `case-studies/jamesdoe-v6/` for their architectural context.

## Original topic 130: Lesson 12 --- Relationship Loading and the N+1 Problem

SQLAlchemy relationships describe how ORM objects are connected, but defining a
relationship does not mean that the related rows are always fetched with the
parent object.

For example, `Product.variants` can exist as an ORM relationship while the
`ProductVariant` rows remain unloaded until the attribute is accessed.

The important distinction is therefore:

``` text
relationship configured
        ≠
relationship data already loaded
```

------------------------------------------------------------------------


## Original topic 131: Lazy Relationship Loading

The default relationship behaviour we observed is **lazy loading**.

A query such as:

``` python
product = session.scalars(
    select(Product).where(Product.id == 1)
).one()
```

loads the `Product`, but does not necessarily load `product.variants`.

Conceptually:

``` text
SELECT product
    ↓
Product object created
    ↓
variants relationship still unloaded
    ↓
product.variants accessed
    ↓
SQLAlchemy issues another SELECT
```

Lazy loading is convenient because related data is only fetched when it is
actually needed. The trade-off is that attribute access can cause database I/O
that is not obvious from the Python expression itself.

A useful Laravel comparison is accessing an Eloquent relationship without
eager-loading it first.

------------------------------------------------------------------------


## Original topic 132: The N+1 Query Problem

Lazy loading becomes particularly important when querying multiple parent
objects.

For example:

``` python
products = session.scalars(select(Product)).all()

for product in products:
    print(product.variants)
```

If the variants relationship is lazy-loaded, the database work can become:

``` text
1 query   → load all Products
N queries → load variants separately for each Product

Total = 1 + N queries
```

For ten products this can mean eleven queries. For one hundred products it can
mean one hundred and one queries.

This is the **N+1 query problem**.

The problem is not the relationship itself. The problem is repeatedly
lazy-loading the relationship while iterating over a collection of parent
objects.

------------------------------------------------------------------------


## Original topic 133: Eager Loading with `selectinload()`

When we know in advance that related rows will be needed, SQLAlchemy can load
them eagerly.

For collection relationships such as `Product.variants`, we used:

``` python
from sqlalchemy.orm import selectinload

product = session.scalars(
    select(Product)
    .options(selectinload(Product.variants))
    .where(Product.id == 1)
).one()
```

`selectinload()` tells SQLAlchemy that the relationship should be populated as
part of executing this query rather than waiting for later attribute access.

Conceptually, for multiple products:

``` text
Query 1
SELECT products ...

Query 2
SELECT product_variants ...
WHERE product_id IN (...)
```

So instead of:

``` text
1 + N queries
```

we can often get:

``` text
2 queries
```

for the parent collection and its related collection.

The exact SQL is SQLAlchemy's responsibility; the important application-level
decision is that the relationship is deliberately requested up front.

------------------------------------------------------------------------


## Original topic 134: `selectinload()` Does Not Mean SQL JOIN

The word **eager** describes *when* related data is loaded, not necessarily *how*
it is loaded.

`selectinload()` normally uses a separate SELECT for the related rows. It does
not combine the parent and child rows into one large result set.

Conceptually:

``` text
selectinload()

SELECT parents
        +
SELECT children WHERE parent_id IN (...)
```

This is useful for one-to-many and many-to-many collection relationships
because it avoids repeating parent rows in a joined result while still avoiding
the N+1 pattern.

------------------------------------------------------------------------


## Original topic 135: `joinedload()`

SQLAlchemy also provides `joinedload()`.

Conceptually:

``` python
from sqlalchemy.orm import joinedload

select(Product).options(joinedload(Product.variants))
```

This asks SQLAlchemy to load the relationship using a JOIN as part of the query.

The rough distinction is:

``` text
selectinload()  → parent SELECT + related SELECT using IN (...)
joinedload()    → parent and related rows loaded through a JOIN
```

Neither strategy is universally better. The appropriate loader depends on the
relationship shape and query. For JamesDoe V6, `selectinload()` is a strong
default for collection relationships when we know the collection will be
needed.

------------------------------------------------------------------------


## Original topic 136: Session Lifetime and Lazy Loading

Lazy loading requires an active ORM context capable of going back to the
database. This became clear in our detached-object experiment.

We first loaded a product without eager-loading its variants:

``` python
session = SessionLocal()

product = session.scalars(
    select(Product).where(Product.id == 1)
).one()

session.close()
```

At that point the `Product` object still existed as a normal Python object, but
it was detached from the Session.

Trying to access an unloaded relationship:

``` python
product.variants
```

produced `DetachedInstanceError`.

The reason was not that detached ORM objects cease to exist. The problem was
that `variants` had not been loaded, and SQLAlchemy would have needed the Session
to perform the lazy-loading query.

Conceptually:

``` text
Product loaded
    ↓
variants UNLOADED
    ↓
Session closed
    ↓
Product becomes detached
    ↓
product.variants
    ↓
needs database query
    ↓
no active Session available
    ↓
DetachedInstanceError
```

------------------------------------------------------------------------


## Original topic 137: Eager Loading Before Detaching

We then repeated the experiment using `selectinload()`:

``` python
session = SessionLocal()

product = session.scalars(
    select(Product)
    .options(selectinload(Product.variants))
    .where(Product.id == 1)
).one()

session.close()
```

After closing the Session:

``` python
product.variants
```

still worked, and:

``` python
[(v.id, v.title) for v in product.variants]
```

returned:

``` text
[(2, 'A2 Print'), (1, 'A3 Print')]
```

This proves that the relationship objects had already been materialised before
the Session was closed.

Conceptually:

``` text
Product loaded
    +
selectinload(Product.variants)
    ↓
Product + variants LOADED
    ↓
Session closed
    ↓
objects detached
    ↓
product.variants
    ↓
already present in memory
    ↓
works without another query
```

The important qualification is that this does **not** make a detached ORM object
capable of loading arbitrary additional data. Only state that was already
loaded remains directly available. Accessing some other unloaded relationship
after the Session has closed can still require database access and therefore
fail.

------------------------------------------------------------------------


## Original topic 138: Relationship Loading Is a Query Decision

A useful architectural lesson from this is that relationship loading should be
driven by the use case.

For example:

``` text
GET /products
    → perhaps product summary data only
    → variants may not be needed

GET /products/{id}
    → product detail response includes variants
    → load variants deliberately
```

We therefore do not need to configure every relationship to be eagerly loaded
globally. Query-specific loader options allow the application to request the
data required by a particular operation.

This keeps database behaviour explicit and avoids both unnecessary loading and
accidental N+1 queries.

------------------------------------------------------------------------


## Original topic 139: Laravel / SQLAlchemy Mental Mapping

The rough conceptual mapping is:

``` text
Laravel / Eloquent                 SQLAlchemy
---------------------------------  -----------------------------------
relationship method/property       relationship()
lazy relationship access           lazy relationship loading
with('variants')                    selectinload(Product.variants)
eager loading                       eager loading
N+1 problem                         N+1 problem
model outside useful ORM context    detached ORM object
```

The APIs differ, but the performance problem and the reason for eager loading
are fundamentally the same.

------------------------------------------------------------------------


## Original topic 140: Lesson 12 Checkpoint

Lesson 12 --- **Relationship Loading and the N+1 Problem** is complete.

The core concepts established are:

``` text
relationship configured           ≠ relationship data loaded

lazy loading                      → load relationship when accessed
eager loading                     → deliberately load relationship up front
selectinload(...)                  → eager load using additional SELECT(s)
joinedload(...)                    → eager load through a JOIN
N+1                               → one parent query + repeated relationship queries

open Session + unloaded relation  → lazy loading can query database
closed Session + unloaded relation
                                  → DetachedInstanceError when loading is required
closed Session + loaded relation  → already-loaded objects remain usable
```

The practical rule for JamesDoe V6 is:

``` text
Do not eager-load every relationship automatically.

Load relationships deliberately when the application operation needs them,
and watch collection queries for accidental N+1 behaviour.
```

Current checkpoint:

``` text
Lesson 7  — First SQLAlchemy ORM Model                    ✓
Lesson 8  — Remaining Core Models                         ✓
Lesson 9  — Relationships Without Database Foreign Keys   ✓
Lesson 10 — Querying with SQLAlchemy                      ✓
Lesson 11 — Writing Data and Unit of Work                 ✓
Lesson 12 — Relationship Loading and N+1                  ✓
```

------------------------------------------------------------------------
