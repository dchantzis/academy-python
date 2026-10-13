from fastapi import FastAPI
from fastapi.testclient import TestClient

def test_health_endpoint():
    app = FastAPI()
    @app.get("/health")
    def health():
        return {"status": "ok"}
    assert TestClient(app).get("/health").json() == {"status": "ok"}
