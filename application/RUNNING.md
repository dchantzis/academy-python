# Running the academy

The recommended workflow is Docker, from the **repository root**. See `../README.md`.

```bash
cp .env.example .env
./dev build
./dev up
./dev test
./dev lesson 12
```

For direct host execution, use `uv sync` and `uv run pytest` inside `application/`.
