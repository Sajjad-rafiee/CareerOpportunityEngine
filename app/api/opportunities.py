"""
Endpoint های مربوط به Opportunity. این فایل عمداً "نازک"‌ه: فقط
پارامترهای درخواست رو می‌گیره، به app.services.opportunities پاس
می‌ده، و نتیجه رو به schema پاسخ تبدیل می‌کنه — هیچ کوئری یا منطق
تجاری‌ای مستقیم اینجا نیست.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.opportunity import (
    OpportunityResponse,
    OpportunitySearchResult,
    PaginatedOpportunities,
)
from app.services.embeddings import embed_text
from app.services.opportunities import list_opportunities, search_opportunities

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=PaginatedOpportunities)
def get_opportunities(
    limit: int = Query(20, ge=1, le=100, description="تعداد رکورد در هر صفحه"),
    offset: int = Query(0, ge=0, description="تعداد رکورد رد شده از اول"),
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
    q: str = Query(..., min_length=1, description="عبارت جستجوی معنایی"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[OpportunitySearchResult]:
    query_embedding = embed_text(q)
    results = search_opportunities(db, query_embedding=query_embedding, limit=limit)

    return [
        OpportunitySearchResult(
            **OpportunityResponse.model_validate(opportunity).model_dump(),
            score=score,
        )
        for opportunity, score in results
    ]
