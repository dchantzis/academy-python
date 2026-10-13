# Lesson authoring conventions

1. Preserve the original learning history for Lessons 1–12; mark corrections and additions explicitly.
2. Explain each concept, compare with PHP/Laravel where useful, then demonstrate with runnable code.
3. Clearly label newly created examples vs. original exercises.
4. Keep exercises independent of JamesDoe V6 infrastructure and data.
5. Put project-specific decisions under `case-studies/`, not general reference.
6. Test with `uv run pytest` and lint with `uv run ruff check .`.
