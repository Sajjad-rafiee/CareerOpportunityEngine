from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.opportunities import router as opportunities_router
from app.core.logging import setup_logging
from app.services.embeddings import get_embedding_model

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    get_embedding_model()  # load once at startup, not on the first search request
    yield


app = FastAPI(
    title="CareerOpportunityEngine",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(opportunities_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "CareerOpportunityEngine is running"}