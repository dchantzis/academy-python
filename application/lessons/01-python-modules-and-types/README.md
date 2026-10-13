# Lesson 01 — Python Modules And Types

Migrated from the original Python Backend Foundations learning notes. Original topic numbers are retained; topic order here is grouped by lesson rather than original chronology.

These notes include JamesDoe V6-specific observations from the original learning sessions; see `case-studies/jamesdoe-v6/` for their architectural context.

## Original topic 4: Python Modules

A Python `.py` file is generally called a **module**.

For example:

``` text
app/
├── main.py
└── config.py
```

`main.py` is a module.

`config.py` is another module.

If `config.py` contains:

``` python
settings = Settings()
```

then `main.py` can import it:

``` python
from app.config import settings
```

Read this almost literally:

``` text
from the `app` package
→ find the `config` module
→ import the thing named `settings`
```

------------------------------------------------------------------------


## Original topic 5: Python Packages and `__init__.py`

A directory containing related Python modules can be a **package**.

For example:

``` text
app/
├── __init__.py
├── main.py
├── config.py
└── database/
    ├── __init__.py
    └── session.py
```

Here:

``` text
app                   package
app.main              module
app.config            module

app.database          package
app.database.session  module
```

For this project, we use an `__init__.py` file to make the package
structure explicit.

The file can be completely empty.

For example:

``` text
database/
├── __init__.py
└── session.py
```

allows code to import something from `session.py` with an import such
as:

``` python
from app.database.session import get_db
```

A useful, although imperfect, PHP mental mapping is:

``` text
PHP namespace/source structure
        ≈
Python package structure
```

This will become more intuitive through repeated use rather than
memorisation.

------------------------------------------------------------------------


## Original topic 6: Python Type Annotations

Consider:

``` python
db_host: str = "database"
```

This breaks down into:

``` text
db_host       field name
: str         expected type
= "database"  default value
```

`: str` is called a **type annotation** or **type hint**.

A rough PHP equivalent would be:

``` php
public string $dbHost = 'database';
```

Other examples will include:

``` python
db_port: int = 5432
```

Here:

``` text
int → integer
str → string
```

Python itself does not always enforce type annotations at runtime.

However, libraries such as Pydantic actively use these annotations for
validation and conversion.

------------------------------------------------------------------------


## Original topic 26: Python Functions and `def`

Python defines a function or method using `def`:

``` python
def database_url(self) -> str:
    ...
```

A rough PHP mapping is:

``` php
public function getDatabaseUrl(): string
{
    // ...
}
```

The `-> str` is the return type annotation: the function is expected to
return a string.

------------------------------------------------------------------------


## Original topic 27: `self`

Inside a Python instance method, `self` refers to the current object.

``` text
PHP          Python

$this   ≈    self
```

For example:

``` php
$this->dbHost
```

maps roughly to:

``` python
self.db_host
```

Python explicitly includes `self` in the method parameter list, but
callers do not manually pass it.

------------------------------------------------------------------------


## Original topic 28: `@property`

A normal method would be called with parentheses:

``` python
settings.database_url()
```

Adding `@property`:

``` python
@property
def database_url(self) -> str:
    ...
```

allows the calculated result to be accessed like an attribute:

``` python
settings.database_url
```

Python still executes the function when the property is accessed.

``` text
Without @property        With @property

database_url()           database_url
method                   property
```

This suits the database URL because it is a **derived value**,
calculated from the individual database settings, rather than an action.

`@property` is a Python **decorator**. We do not need to learn
decorators in depth yet; they will appear naturally again later.

------------------------------------------------------------------------


## Original topic 29: Python f-Strings

A string prefixed with `f` is a Python **formatted string literal**,
usually called an **f-string**.

``` python
name = "Dimitris"

message = f"Hello {name}"
```

produces:

``` text
Hello Dimitris
```

Without the `f`, `{name}` would remain ordinary text.

The closest familiar concept is PHP string interpolation:

``` text
PHP                         Python

"Hello {$name}"             f"Hello {name}"
"ID: {$user->id}"           f"ID: {user.id}"
```

Expressions inside `{...}` are evaluated and inserted:

``` python
price = 10
message = f"The total is {price * 2}"
```

produces:

``` text
The total is 20
```

Adjacent Python string literals are automatically joined. This lets us
split the database URL over two readable lines:

``` python
return (
    f"postgresql+psycopg://{self.db_user}:{self.db_password}"
    f"@{self.db_host}:{self.db_port}/{self.db_database}"
)
```

The two f-strings become one string.

------------------------------------------------------------------------


## Original topic 34: Python `with` and Context Managers

We verified the Engine manually:

``` python
with engine.connect() as connection:
    print("Connected to PostgreSQL")
```

`with` is Python syntax for using a **context manager**. A useful mental
model is:

> Obtain a resource, use it inside the indented block, and perform the
> appropriate cleanup when the block ends.

This is roughly comparable in purpose to resource acquisition combined
with `try/finally` cleanup in PHP.

Python indentation defines the block; braces are not used.

------------------------------------------------------------------------


## Original topic 36: `close()` and Method Calls

Calling:

``` python
session.close()
```

does not destroy the Python object. It cleans up/resets the Session's
current database resources, including releasing checked-out connections.

We also observed:

``` text
session.close     → refer to the method itself
session.close()   → call/execute the method
```

The parentheses matter. This is a general Python distinction, not a
SQLAlchemy-specific rule.

------------------------------------------------------------------------


## Original topic 37: `yield` and Generator Functions

Our request-scoped dependency is:

``` python
def get_db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
```

Compare:

``` text
return
    → provide value
    → function finishes

yield
    → provide value
    → function pauses
    → caller uses value
    → function can resume
```

A function containing `yield` is a **generator function**.

Calling:

``` python
db = get_db()
```

creates a generator object rather than immediately returning a Session.

------------------------------------------------------------------------


## Original topic 38: `next()` and `StopIteration`

We explored the generator manually.

``` python
db = get_db()
session = next(db)
```

The first `next(db)` starts `get_db()`, creates the Session, reaches
`yield session`, returns that Session, and pauses.

Calling:

``` python
next(db)
```

again resumes after `yield`, executes the `finally` block, closes the
Session, reaches the end of the generator, and raises `StopIteration`.

We do not manually use `next()` in the FastAPI application. This
experiment showed what FastAPI manages for us.

------------------------------------------------------------------------


## Original topic 39: `try` / `finally`

Python's `try` / `finally` has the same fundamental purpose as PHP's.

``` python
try:
    yield session
finally:
    session.close()
```

The `finally` block provides reliable cleanup when the dependency
finishes, including when request processing raises an exception.

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

