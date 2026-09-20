from fastapi import FastAPI

from app.api.opportunities import router as opportunities_router
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title="CareerGraphAI",
    version="0.1.0",
)

app.include_router(opportunities_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "CareerGraphAI is running"}