# Lesson 10 — Querying With Sqlalchemy

Migrated from the original Python Backend Foundations learning notes. Original topic numbers are retained; topic order here is grouped by lesson rather than original chronology.

These notes include JamesDoe V6-specific observations from the original learning sessions; see `case-studies/jamesdoe-v6/` for their architectural context.

## Original topic 99: Lesson 10: Querying with SQLAlchemy

Lesson 10 introduced the SQLAlchemy 2.x ORM querying workflow against
the real JamesDoe V6 PostgreSQL database.

The fundamental pattern is:

``` python
from sqlalchemy import select

statement = select(Collection)
collections = session.scalars(statement).all()
```

The important separation is:

``` text
select(...)
    → build a SQLAlchemy Select object
    → no database access yet

Session execution
    → execute the statement against PostgreSQL
    → obtain results
```

For example:

``` python
statement = select(Collection)
```

produces a `sqlalchemy.sql.selectable.Select` object. Printing it shows
the SQLAlchemy-generated SQL, with the mapped columns listed explicitly
rather than using `SELECT *`.

------------------------------------------------------------------------


## Original topic 100: `execute()`, Result Rows, and `scalars()`

A statement can be executed through the Session:

``` python
result = session.execute(statement)
```

The flow is:

``` text
Select object
    ↓
Session.execute(...)
    ↓
Engine
    ↓
Psycopg
    ↓
PostgreSQL
    ↓
Result
```

`execute()` is a general-purpose API and works in terms of result rows.
When selecting one ORM entity:

``` python
select(Collection)
```

a result row conceptually contains one selected value:

``` text
(Collection(...),)
```

`scalars()` extracts that selected value from each result row:

``` python
result = session.execute(statement)
collections = result.scalars().all()
```

SQLAlchemy also provides the convenient ORM-oriented form:

``` python
collections = session.scalars(statement).all()
```

A useful mental model is:

``` text
execute(...)      → result rows
scalars()         → selected value from each row
all()             → collect all values into a Python list
```

Here, "scalar" does not mean only a primitive value such as an integer
or string. A `Collection` ORM object can be the scalar value because it
is the single selected thing in each result row.

------------------------------------------------------------------------


## Original topic 101: Lists, Tuples, and List Comprehensions

Lesson 10 also introduced a few Python collection concepts while
inspecting query results.

A list uses square brackets and is mutable:

``` python
item = [1, "Coffee & Sketch"]
item[1] = "Archive"
```

A tuple normally uses parentheses and is immutable:

``` python
item = (1, "Coffee & Sketch")
```

A useful starting mental model is:

``` text
list  []  → mutable collection of things
tuple ()  → fixed grouping of things
```

PHP arrays do not have this exact distinction.

We also used a list comprehension:

``` python
result = [
    (collection.id, collection.title)
    for collection in collections
]
```

which is a compact form of:

``` python
result = []

for collection in collections:
    result.append((collection.id, collection.title))
```

The outer value is a list; each `(id, title)` value is a tuple.

------------------------------------------------------------------------


## Original topic 102: Filtering with `where()` and Bound Parameters

SQLAlchemy filtering uses `where()`:

``` python
statement = select(Collection).where(
    Collection.slug == "coffee-and-sketch"
)
```

This produces SQL resembling:

``` sql
WHERE collections.slug = :slug_1
```

`Collection.slug == "coffee-and-sketch"` does not immediately evaluate
to a Python boolean. `Collection.slug` is a SQLAlchemy mapped attribute,
so the comparison constructs a SQL expression.

`:slug_1` is a bound parameter. SQLAlchemy passes the value separately
to the database driver rather than manually interpolating it into the
SQL string.

Multiple conditions passed to `where()` are combined with `AND`:

``` python
statement = select(Collection).where(
    Collection.slug == "coffee-and-sketch",
    Collection.is_visible.is_(True),
)
```

Chaining `where()` calls is equivalent:

``` python
statement = (
    select(Collection)
    .where(Collection.slug == "coffee-and-sketch")
    .where(Collection.is_visible.is_(True))
)
```

For boolean SQL expressions we used:

``` python
Collection.is_visible.is_(True)
Collection.is_visible.is_(False)
```

------------------------------------------------------------------------


## Original topic 103: Retrieving Many, One, or No Results

SQLAlchemy provides different result methods depending on the
cardinality the application expects.

``` text
Method          0 rows       1 row         2+ rows

.all()          []           [obj]         [obj, obj...]
.first()        None         obj           first obj
.one_or_none()  None         obj           MultipleResultsFound
.one()          NoResultFound obj          MultipleResultsFound
```

For example:

``` python
collection = session.scalars(statement).one_or_none()
```

means that zero or one result is valid, but multiple results violate the
query's expected cardinality.

For a unique field such as `Collection.slug`, `one_or_none()` clearly
expresses that expectation.

We deliberately called:

``` python
session.scalars(statement).one()
```

against an empty table and observed:

``` text
sqlalchemy.exc.NoResultFound:
No row was found when one was required
```

------------------------------------------------------------------------


## Original topic 104: Ordering and Limiting

Ordering uses `order_by()`:

``` python
statement = (
    select(Collection)
    .where(Collection.is_visible.is_(True))
    .order_by(Collection.sort_order)
)
```

Descending order uses:

``` python
.order_by(Collection.sort_order.desc())
```

Limiting uses:

``` python
.limit(10)
```

For example:

``` python
statement = (
    select(Collection)
    .where(Collection.is_visible.is_(True))
    .order_by(Collection.sort_order)
    .limit(10)
)
```

A useful naming convention is to distinguish the unexecuted statement
from the executed result:

``` python
statement = select(Collection)
collections = session.scalars(statement).all()
```

After `.all()`, `collections` is a Python `list`; it is no longer a
SQLAlchemy statement.

------------------------------------------------------------------------


## Original topic 105: Creating Query Data During Lesson 10

The database was initially empty, so we created two real `Collection`
rows to make the query exercises meaningful:

``` python
from uuid import uuid4

coffee_and_sketch = Collection(
    uuid=uuid4(),
    title="Coffee & Sketch",
    slug="coffee-and-sketch",
    description="Coffee & Sketch publications and artwork.",
    is_visible=True,
    sort_order=10,
)

archive = Collection(
    uuid=uuid4(),
    title="Archive",
    slug="archive",
    description="Archived artwork.",
    is_visible=False,
    sort_order=20,
)
```

Before persistence:

``` text
coffee_and_sketch.id → None
archive.id           → None
```

We temporarily borrowed two write operations from Lesson 11:

``` python
session.add(coffee_and_sketch)
session.add(archive)
session.commit()
```

After the commit, PostgreSQL-generated values were available on the same
ORM objects:

``` text
coffee_and_sketch.id → 1
archive.id           → 2
```

The `created_at` values were also populated from the PostgreSQL
`server_default=func.now()` definition.

The mechanics of `add()`, flushing, committing, generated values, and
the Unit of Work are intentionally deferred to Lesson 11.

------------------------------------------------------------------------


## Original topic 106: ORM Objects Returned from Real Queries

With persisted data, this query:

``` python
collections = session.scalars(
    select(Collection)
    .where(Collection.is_visible.is_(True))
    .order_by(Collection.sort_order)
).all()
```

returned a Python list containing a real mapped object:

``` text
list[Collection]
```

Attributes can then be accessed normally:

``` python
collections[0].id
collections[0].title
collections[0].slug
```

The complete path is:

``` text
PostgreSQL row
    ↓
Psycopg
    ↓
SQLAlchemy
    ↓
Collection ORM object
    ↓
normal Python attributes
```

------------------------------------------------------------------------


## Original topic 107: Primary-Key Lookup and the Session Identity Map

For a primary-key lookup, SQLAlchemy provides:

``` python
collection = session.get(Collection, 1)
```

This is roughly comparable to:

``` php
Collection::find(1);
```

If the primary key does not exist, `Session.get()` returns `None`.

We then observed:

``` python
collection1 = session.get(Collection, 1)
collection2 = session.get(Collection, 1)

collection1 is collection2
# True

collection1 is coffee_and_sketch
# True
```

Python's `is` asks whether two references point to the exact same Python
object in memory.

The SQLAlchemy Session maintains an **identity map**. Conceptually:

``` text
(Collection, 1) → one Collection Python object
(Collection, 2) → one Collection Python object
```

Within one Session, one database identity corresponds to one Python
object identity. This becomes particularly important when modifying
tracked objects in Lesson 11.

------------------------------------------------------------------------


## Original topic 108: `IN` and `OR` Conditions

SQL `IN` is represented with `in_()`:

``` python
collections = session.scalars(
    select(Collection)
    .where(Collection.id.in_([1, 2]))
    .order_by(Collection.id)
).all()
```

For explicit `OR` expressions, SQLAlchemy provides `or_()`:

``` python
from sqlalchemy import or_

statement = select(Collection).where(
    or_(
        Collection.slug == "coffee-and-sketch",
        Collection.slug == "archive",
    )
)
```

For several possible values of the same column, `in_()` is normally
cleaner:

``` python
Collection.slug.in_(["coffee-and-sketch", "archive"])
```

`or_()` is useful when the alternatives are different conditions, for
example:

``` python
or_(
    Collection.is_visible.is_(True),
    Collection.sort_order > 15,
)
```

------------------------------------------------------------------------


## Original topic 109: `LIKE` and `ILIKE`

SQL text matching is exposed directly by mapped string attributes.

Case-sensitive SQL `LIKE`:

``` python
Collection.title.like("%Sketch%")
```

PostgreSQL case-insensitive `ILIKE`:

``` python
Collection.title.ilike("%sketch%")
```

For example:

``` python
collections = session.scalars(
    select(Collection).where(
        Collection.title.ilike("%sketch%")
    )
).all()
```

matches `Coffee & Sketch` even though the search text uses lowercase.

------------------------------------------------------------------------


## Original topic 110: Pagination with `limit()` and `offset()`

Basic offset pagination uses:

``` python
.limit(per_page)
.offset((page - 1) * per_page)
```

For example:

``` python
page = 2
per_page = 10

statement = (
    select(Collection)
    .order_by(Collection.id)
    .limit(per_page)
    .offset((page - 1) * per_page)
)
```

The offset calculation is:

``` text
offset = (page - 1) * per_page

page 1, 10/page → offset 0
page 2, 10/page → offset 10
page 3, 10/page → offset 20
```

Pagination should use a deterministic `ORDER BY`. SQL does not guarantee
row order without one, so paginating an unordered query can produce
unstable results.

------------------------------------------------------------------------


## Original topic 111: Counting and `Session.scalar()`

Counting introduced SQLAlchemy's SQL function namespace:

``` python
from sqlalchemy import func

statement = select(func.count()).select_from(Collection)
```

which represents:

``` sql
SELECT count(*)
FROM collections
```

Because this query returns one row containing one selected value, we
used the singular Session method:

``` python
count = session.scalar(statement)
```

With the two lesson records:

``` text
all collections     → 2
visible collections → 1
```

A filtered count is:

``` python
visible_count = session.scalar(
    select(func.count())
    .select_from(Collection)
    .where(Collection.is_visible.is_(True))
)
```

Useful distinction:

``` text
session.scalars(...) → potentially many selected scalar values
session.scalar(...)  → one scalar value
```

------------------------------------------------------------------------


## Original topic 112: Lesson 10 Checkpoint

Lesson 10 --- **Querying with SQLAlchemy** is complete.

The core query patterns established are:

``` text
select(Model)             → build an ORM SELECT statement
Session.execute(...)      → execute and obtain result rows
Session.scalars(...)      → execute and expose selected scalar values
.all()                    → all results as a list
.first()                  → first result or None
.one_or_none()            → zero or one; error if multiple
.one()                    → exactly one; error otherwise
Session.get(Model, id)    → primary-key lookup
.where(...)               → filtering
or_(...)                  → OR conditions
.in_(...)                 → SQL IN
.like(...) / .ilike(...)  → text matching
.order_by(...)            → deterministic ordering
.limit(...)               → limit result count
.offset(...)              → offset/pagination
func.count()              → SQL COUNT
Session.scalar(...)       → one scalar result
```

The lesson also established the Session identity map:

``` text
one database identity
        ↓
one Python ORM object per Session
```

and reinforced several Python concepts encountered naturally during
querying:

``` text
list                  → mutable sequence
 tuple                 → immutable/fixed sequence
list comprehension    → compact construction of a list from an iterable
is                    → object identity comparison
```

The next lesson is:

``` text
Lesson 11
Writing Data and Unit of Work
```

------------------------------------------------------------------------

