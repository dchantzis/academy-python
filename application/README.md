# Academy Python

Independent learning repository for Python, FastAPI, SQLAlchemy, Alembic, Pydantic and later Django. Lessons 01–12 are migrated from the completed JamesDoe V6 learning work, **not a new curriculum requiring repetition**.

## Docker quick start

From the repository root:

```bash
cp .env.example .env
./dev build
./dev up
./dev check
./dev lesson 12
```

See `../README.md` for Docker commands and optional PostgreSQL.

## Direct host quick start (optional)

```bash
uv sync
uv run pytest
uv run python lessons/01-python-modules-and-types/examples/fundamentals.py
PYTHONPATH=. uv run python lessons/12-relationship-loading-and-n-plus-one/examples/loading.py
```

Python >=3.13 is supported; Python 3.14 is the intended learning target. `uv.lock` is not bundled: generate it using `uv lock` / `uv sync` in your environment.

## Organisation

- `lessons/01-...` through `12-...`: original learning explanations reorganised by lesson, with source topic numbers retained.
- `lessons/*/examples/`: executable self-contained illustrations; **new educational reconstructions**, not copies of the JamesDoe application.
- `academy_examples/`: small shared SQLAlchemy training model and isolated in-memory SQLite data.
- `tests/`: pytest exercises and example verification.
- `roadmaps/`: original FastAPI/SQLAlchemy, Django, and Python Lab roadmaps (historical status markers may be stale).
- `reference/`: source mapping and selected technical quick references.
- `case-studies/jamesdoe-v6/`: project-specific decisions and real-world context, not universal rules.
- `archive/original-documents/`: original learning documents retained unmodified.

## Scope and provenance

The source foundations guide is a **topic-numbered living notebook**, not twelve independently labelled chapters. We regrouped its 140 topics into lessons, retaining original topic numbers and source material. Topic 23 (locked decisions) and 24 (application structure) live under the case study. Some notes include historical JamesDoe paths and commands; they are documentary, not instructions to execute in this repository.

**No production dependencies:** no imports from `jamesdoe-v6`, no connection to its database, no requirement to run its containers. Training SQLAlchemy examples use SQLite in memory. PostgreSQL-specific migrations remain documented; a separate Postgres lab can be added when needed.

## Next lesson

Lesson 13 — Pydantic API Models. Add it without changing the completed lessons.
