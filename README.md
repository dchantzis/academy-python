# Academy Python — Docker development

The learning materials are in `application/`. The container uses **Python 3.14**, **uv**, pytest, Ruff and a persistent `/opt/venv` dependency volume. No Python installation is required on the host.

## First run

```bash
cp .env.example .env
chmod +x dev
./dev build
./dev up
./dev check
./dev lesson 12
```

Run `./dev help` for the full command reference. `./dev ssh` opens a shell inside the Python container. `./dev python` and `./dev uv` execute their respective commands inside it. `./dev test` runs pytest, and `./dev check` runs pytest and Ruff, printing `OK` when both succeed. `./dev lesson 12` executes the single example for Lesson 12; if a lesson contains multiple examples, use `./dev lesson 12 filename.py`.

## Database exercises

PostgreSQL 17 is **opt-in**, not started by `./dev up`:

```bash
./dev db-up
./dev db-shell
./dev db-down
```

Inside the app container, connect to `database:5432` with the credentials in the root `.env`. No host port is exposed. Existing lessons use isolated in-memory SQLite; they do not require PostgreSQL. Database data persists in a named Docker volume. `./dev purge` **deletes** both dependency and database volumes.

## Environment and dependencies

The root `.env` configures Compose; it is not committed. `application/pyproject.toml` defines dependencies. On first start, `uv sync` generates `application/uv.lock` if it does not exist. Commit that lockfile once generated. On subsequent starts, `uv sync --frozen` uses the lockfile. After changing dependencies, run `./dev uv lock` followed by `./dev bootstrap`.

The container runs as your local UID/GID. The application source is bind-mounted; only `/opt/venv` and the container's temporary home are ownership-adjusted. The app container idles until you run commands; no Uvicorn process starts automatically. For a FastAPI lesson, run Uvicorn explicitly with `./dev python -m uvicorn ...` after adding the required dependency and application entry point.

The repository has no imports or database dependencies on JamesDoe V6.
