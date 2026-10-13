"""Run with: uv run uvicorn lessons/02-fastapi-and-configuration/examples/app:app --reload"""
from fastapi import FastAPI
app = FastAPI(title="Academy Python — FastAPI Example")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
