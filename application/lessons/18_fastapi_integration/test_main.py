"""Lesson 18: HTTP tests with an isolated fake session."""

import importlib.util
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

# The lesson directory starts with a number, so load its module by file path.
spec = importlib.util.spec_from_file_location(
    "lesson18_api", Path(__file__).with_name("main.py")
)
assert spec is not None and spec.loader is not None
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class FakeSession:
    def get(self, model: type, artwork_id: int) -> Any:
        if artwork_id == 42:
            return model(
                id=42,
                title="Moto Rider",
                slug="moto-rider",
                internal_note="Must not appear in JSON",
            )
        return None


def override_get_db():
    yield FakeSession()


@pytest.fixture
def client():
    api.app.dependency_overrides[api.get_db] = override_get_db
    try:
        with TestClient(api.app) as test_client:
            yield test_client
    finally:
        api.app.dependency_overrides.clear()


def test_existing_artwork(client):
    response = client.get("/api/v1/artworks/42")
    assert response.status_code == 200
    assert response.json() == {
        "id": 42,
        "title": "Moto Rider",
        "slug": "moto-rider",
    }
    assert "internal_note" not in response.json()


def test_missing_artwork(client):
    response = client.get("/api/v1/artworks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Artwork not found"}


def test_invalid_path_parameter(client):
    response = client.get("/api/v1/artworks/not-an-integer")
    assert response.status_code == 422
