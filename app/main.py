from fastapi import FastAPI

from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title="CareerGraphAI",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "CareerGraphAI is running"}