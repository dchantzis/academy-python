FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_CACHE_DIR=/tmp/python-home/.cache/uv \
    HOME=/tmp/python-home \
    PYTHONPATH=/var/www \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /var/www
COPY --chmod=755 docker-configuration/entrypoint/start-container /usr/bin/start-container
COPY --chmod=755 docker-configuration/entrypoint/start-container-local /usr/bin/start-container-local
ENTRYPOINT ["/usr/bin/start-container"]
CMD ["sleep", "infinity"]
