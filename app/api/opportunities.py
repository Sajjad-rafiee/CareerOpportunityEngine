"""Opportunity endpoints. Kept thin: parse params, call services, shape response."""

import time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.opportunity import (
    OpportunityResponse,
    OpportunitySearchResult,
    PaginatedOpportunities,
)
from app.services.embeddings import embed_text
from app.services.opportunities import list_opportunities, search_opportunities

router = APIRouter(prefix="/opportunities", tags=["opportunities"])

# Local-only observability demo fault injection (OTEL_DEMO_FAULT_MODE, default
# "none"): produces a real slow/failing trace on demand, never in normal use.
_DEMO_FAULT_DELAY_SECONDS = 2.0


def _apply_demo_fault() -> None:
    mode = get_settings().otel_demo_fault_mode
    if mode == "delay":
        time.sleep(_DEMO_FAULT_DELAY_SECONDS)
    elif mode == "error":
        raise HTTPException(status_code=503, detail="Demo fault injection: simulated outage")


@router.get("", response_model=PaginatedOpportunities)
def get_opportunities(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> PaginatedOpportunities:
    items, total = list_opportunities(db, limit=limit, offset=offset)

    return PaginatedOpportunities(
        items=[OpportunityResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/search", response_model=list[OpportunitySearchResult])
def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[OpportunitySearchResult]:
    _apply_demo_fault()

    query_embedding = embed_text(q)
    results = search_opportunities(db, query_embedding=query_embedding, limit=limit)

    return [
        OpportunitySearchResult(
            **OpportunityResponse.model_validate(opportunity).model_dump(),
            score=score,
        )
        for opportunity, score in results
    ]
