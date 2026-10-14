"""Lesson 17: pytest fixtures, HTTP tests, parametrization and DI overrides."""

import pytest
from fastapi.testclient import TestClient

from main import ArtworkRepository, app, get_repository


@pytest.fixture
def client():
    # Each test receives a fresh repository: no state leaks between tests.
    test_repository = ArtworkRepository()
    app.dependency_overrides[get_repository] = lambda: test_repository
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def test_get_existing_artwork(client):
    response = client.get("/artworks/42")
    assert response.status_code == 200
    assert response.json() == {"id": 42, "title": "Moto Rider", "price": 150.0}


def test_get_missing_artwork(client):
    response = client.get("/artworks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Artwork not found"}


@pytest.mark.parametrize("price,expected_status", [(100, 201), (0, 201), (-10, 422)])
def test_price_validation(client, price, expected_status):
    response = client.post("/artworks", json={"title": "New Artwork", "price": price})
    assert response.status_code == expected_status
    if expected_status == 201:
        assert response.json()["title"] == "New Artwork"
        assert response.json()["price"] == price
        assert "id" in response.json()


def test_invalid_path_parameter(client):
    response = client.get("/artworks/not-an-integer")
    assert response.status_code == 422
