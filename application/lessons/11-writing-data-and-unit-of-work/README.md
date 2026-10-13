# Lesson 11 — Writing Data And Unit Of Work

Migrated from the original Python Backend Foundations learning notes. Original topic numbers are retained; topic order here is grouped by lesson rather than original chronology.

These notes include JamesDoe V6-specific observations from the original learning sessions; see `case-studies/jamesdoe-v6/` for their architectural context.

## Original topic 113: Lesson 11: Writing Data and Unit of Work

Lesson 11 introduced SQLAlchemy's write lifecycle and the **Unit of
Work** model. Rather than treating each model write as an isolated
operation, a `Session` tracks the objects and changes that belong to the
current unit of database work.

The core lifecycle encountered during the lesson was:

``` text
TRANSIENT
    │
    │ session.add()
    ▼
PENDING
    │
    │ flush / INSERT
    ▼
PERSISTENT
```

SQLAlchemy object state can be inspected with:

``` python
from sqlalchemy import inspect

state = inspect(obj)

state.transient
state.pending
state.persistent
state.deleted
```

------------------------------------------------------------------------


## Original topic 114: Transient ORM Objects

Constructing an ORM object creates an ordinary Python object but does
not persist anything:

``` python
new_collection = Collection(
    uuid=uuid4(),
    title="Motorcycles",
    slug="motorcycles",
    description="Motorcycle artwork.",
    is_visible=True,
    sort_order=30,
)
```

At this point:

``` text
transient   → True
pending     → False
persistent  → False
id          → None
```

`transient` means the ORM object exists in Python but is not currently
part of a SQLAlchemy Session and has not been persisted.

------------------------------------------------------------------------


## Original topic 115: `Session.add()` and Pending State

Calling:

``` python
session.add(new_collection)
```

registers the object with the Session's Unit of Work.

Its state becomes:

``` text
transient   → False
pending     → True
persistent  → False
```

`Session.add()` does not necessarily issue an `INSERT` immediately. It
tells the Session that the object should be persisted when the Unit of
Work is flushed.

Pending objects can also be observed through:

``` python
new_collection in session.new
```

The useful mental model is:

``` text
Session
├── new objects
├── modified objects
└── objects scheduled for deletion
```

------------------------------------------------------------------------


## Original topic 116: `flush()` vs `commit()`

Calling:

``` python
session.flush()
```

synchronises the Session's current Unit of Work with PostgreSQL **inside
the current transaction**.

For a pending object this means an `INSERT` is issued. After the flush:

``` text
pending     → False
persistent  → True
```

Database-generated values such as the identity primary key become
available:

``` python
new_collection.id
```

The important distinction is:

``` text
flush()
    → send pending INSERT / UPDATE / DELETE work to PostgreSQL
    → remain inside the current transaction

commit()
    → flush pending work if necessary
    → COMMIT the transaction
    → make the transaction permanent
```

Therefore:

``` text
flush() ≠ commit()
```

A flushed change can still be rolled back.

------------------------------------------------------------------------


## Original topic 117: Rollback After a Flushed INSERT

After flushing a new object, calling:

``` python
session.rollback()
```

reverses the database transaction. The inserted row does not remain in
PostgreSQL.

A newly inserted object that is rolled back returns to a transient
state. Values that were populated onto the Python object during the
flush, such as a generated identity value, may still remain on the
ordinary Python attribute.

This reinforces an important distinction:

``` text
Python object state ≠ committed database state
```

PostgreSQL identity/sequence values are not intended to be gapless. An
identity value consumed by an insert that is later rolled back can
therefore leave a gap.

------------------------------------------------------------------------


## Original topic 118: `commit()` Automatically Flushes

A normal insert can be written as:

``` python
session.add(new_collection)
session.commit()
```

An explicit `flush()` is not required before `commit()` because commit
flushes pending changes first.

Conceptually:

``` text
session.commit()
      │
      ├── flush
      │     ↓
      │   INSERT / UPDATE / DELETE
      │
      └── COMMIT
            ↓
      transaction permanent
```

During the lesson the successfully committed `Motorcycles` collection
received ID `4` and could subsequently be queried from PostgreSQL.

------------------------------------------------------------------------


## Original topic 119: Failed Flushes and `PendingRollbackError`

The lesson encountered a useful real failure when the object was
accidentally constructed with:

``` python
uuid=uuid4
```

instead of:

``` python
uuid=uuid4()
```

The first form stores the **function itself**. The second calls the
function and stores the returned UUID.

Psycopg therefore rejected the first value:

``` text
cannot adapt type 'function'
```

Because `session.commit()` automatically flushes, the error happened
during the commit's flush phase.

After a flush/commit failure, the Session's transaction is in a failed
state. Before the Session can be used again, call:

``` python
session.rollback()
```

Otherwise SQLAlchemy raises `PendingRollbackError`.

The practical rule is:

> If a SQLAlchemy flush or commit fails, roll back the Session before
> trying to continue using it.

------------------------------------------------------------------------


## Original topic 120: Dirty Tracking for Updates

Persistent ORM objects are tracked by their Session. Updating a mapped
attribute is therefore enough to make the object dirty:

``` python
motorcycles.description = "Motorcycles, cafe racers and rider artwork."
```

The Session can report this:

``` python
session.is_modified(motorcycles)
# True

motorcycles in session.dirty
# True
```

There is no Eloquent-style requirement to call a model-level `save()`
method. The Session's Unit of Work detects the mapped attribute change
and issues the required `UPDATE` when it flushes.

A rough comparison is:

``` text
Eloquent
    object.attribute = value
    object.save()

SQLAlchemy
    object.attribute = value
    Session tracks the change
    Session flushes/commits the Unit of Work
```

------------------------------------------------------------------------


## Original topic 121: Attribute Change History

SQLAlchemy can expose pending attribute history:

``` python
state = inspect(motorcycles)
state.attrs.description.history
```

Before a flush, a fully loaded previous value can produce history such
as:

``` text
History(
    added=['Motorcycles, cafe racers and rider artwork.'],
    unchanged=(),
    deleted=['Motorcycle and cafe-racer artwork.']
)
```

Here `deleted` means the old attribute value was replaced. It does not
mean the row or column was deleted.

After `flush()` the new value becomes the Session's synchronised
transaction state:

``` text
History(
    added=(),
    unchanged=['Motorcycles, cafe racers and rider artwork.'],
    deleted=()
)
```

Attribute history describes the ORM's current change state; it is not a
permanent audit log.

We also observed that after a commit SQLAlchemy may expire attributes by
default. If the previous value has not been loaded again before
replacement, that old value may not appear in `history.deleted`.

------------------------------------------------------------------------


## Original topic 122: Rollback After a Flushed UPDATE

The update lifecycle observed was:

``` text
modify mapped attribute
        ↓
object becomes DIRTY
        ↓
flush()
        ↓
UPDATE sent to PostgreSQL
        ↓
object no longer dirty
        ↓
transaction still open
        ↓
rollback()
        ↓
UPDATE reversed
```

After rollback, reading the attribute returned the previously committed
value:

``` text
'Motorcycle and cafe-racer artwork.'
```

This demonstrates that `flush()` synchronises with the **current
transaction**; it does not make the update permanent.

------------------------------------------------------------------------


## Original topic 123: Deleting ORM Objects

A persistent object can be scheduled for deletion with:

``` python
session.delete(motorcycles)
```

Before flushing:

``` python
motorcycles in session.deleted
# True
```

but inspection showed:

``` text
state.persistent → True
state.deleted    → False
```

This means the object is still persistent but is scheduled for deletion
by the Unit of Work.

After:

``` python
session.flush()
```

we observed:

``` text
motorcycles in session.deleted → False
state.persistent               → False
state.deleted                  → True
```

The distinction is:

``` text
Before flush
    session.deleted → objects waiting for DELETE
    state.deleted   → False

After flush
    DELETE has been issued
    session.deleted → False
    state.deleted   → True
```

------------------------------------------------------------------------


## Original topic 124: Rollback After a Flushed DELETE

Because the DELETE had only been flushed, it could still be reversed:

``` python
session.rollback()
```

The `Motorcycles` collection remained queryable afterward.

The query returned the same Python ORM object:

``` python
motorcycles_again is motorcycles
# True
```

This connects Lesson 11 back to Lesson 10's Session identity map:

``` text
(Collection, 4)
      ↓
same Python object within the Session
```

Rollback restored the object's persistent database state without
creating a replacement ORM instance.

------------------------------------------------------------------------


## Original topic 125: The SQLAlchemy Unit of Work

The Session can coordinate several kinds of change together:

``` python
session.add(new_collection)

motorcycles.title = "Motorcycle Art"

session.delete(archive)
```

Conceptually the Session now tracks:

``` text
Session
│
├── NEW
│   └── new_collection
│
├── DIRTY
│   └── motorcycles
│
└── DELETED
    └── archive
```

A flush synchronises the complete Unit of Work:

``` text
INSERT new_collection
UPDATE motorcycles
DELETE archive
```

within the same database transaction.

The transaction can then be resolved with either:

``` text
commit()
    → make the transaction permanent

rollback()
    → discard the transaction
```

This is the central Lesson 11 mental model: the SQLAlchemy Session
coordinates object identity, change tracking, persistence operations,
and the current Unit of Work.

------------------------------------------------------------------------


## Original topic 126: Session Lifetime in FastAPI Requests

JamesDoe V6 already uses the request-scoped dependency:

``` python
def get_db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
```

The lifecycle is:

``` text
HTTP request
    ↓
get_db()
    ↓
SessionLocal()
    ↓
yield Session
    ↓
endpoint/application work
    ↓
get_db() resumes
    ↓
finally
    ↓
session.close()
```

This implements the locked architecture decision:

> One SQLAlchemy Session per HTTP request.

A single request can therefore perform several related database
operations as one coherent Unit of Work.

For example:

``` text
create Artwork
create Image
create ArtworkImage
create Product
create ProductVariant
        ↓
one transaction
        ↓
commit all or rollback all
```

------------------------------------------------------------------------


## Original topic 127: `close()` Is Not `commit()`

Session lifetime and transaction outcome are separate responsibilities.

``` python
session.close()
```

means that the application has finished using that Session and its
resources should be cleaned up/released.

It does **not** mean:

``` text
save whatever happened during this request
```

The important separation is:

``` text
commit()    → make current transaction permanent
rollback()  → discard current transaction
close()     → finish using/clean up the Session
```

------------------------------------------------------------------------


## Original topic 128: Transaction Boundary Decision for JamesDoe V6

Two broad patterns were considered.

A request dependency could automatically commit or roll back around
every request, or application/service code could explicitly control the
transaction.

For now, JamesDoe V6 keeps `get_db()` responsible only for Session
lifetime:

``` python
def get_db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
```

Transaction decisions remain explicit in the application/service
operation. Conceptually:

``` text
get_db()
    → how long does this Session live?

application/service operation
    → should this Unit of Work commit or rollback?
```

This keeps transaction behaviour visible while the application layer is
still being developed. A more abstract transaction boundary can be
introduced later if real application code justifies it.

------------------------------------------------------------------------


## Original topic 129: Lesson 11 Checkpoint

Lesson 11 --- **Writing Data and Unit of Work** is complete.

The core concepts established are:

``` text
transient                 → Python ORM object not attached to a Session
pending                   → added to Session; awaiting INSERT
persistent                → ORM object represents persistent Session state
dirty                     → persistent object has pending mapped changes
deleted                   → DELETE has been flushed for the object

Session.add(...)          → register a new object with the Unit of Work
Session.delete(...)       → schedule persistent object for deletion
Session.flush()           → synchronise pending SQL inside current transaction
Session.commit()          → flush if necessary, then commit transaction
Session.rollback()        → reverse current transaction
Session.close()           → finish using/clean up Session resources

session.new               → pending new objects
session.dirty             → tracked modified objects
session.deleted           → objects scheduled for deletion
session.is_modified(...)  → ask whether mapped state has changed
inspect(obj)              → inspect ORM object state and attribute history
```

The complete write lifecycle can be summarised as:

``` text
INSERT
transient
    ↓ add()
pending
    ↓ flush()
persistent

UPDATE
persistent
    ↓ attribute assignment
dirty
    ↓ flush()
persistent / synchronised

DELETE
persistent
    ↓ delete()
scheduled for deletion
    ↓ flush()
deleted
```

And the transaction boundary is:

``` text
Unit of Work
    ↓
flush()
    ↓
SQL synchronised inside transaction
    ↓
┌───────────────┬────────────────┐
│ commit()      │ rollback()     │
│ permanent     │ discard        │
└───────────────┴────────────────┘
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

