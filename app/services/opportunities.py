"""Opportunity queries. Kept out of the API layer so routes stay thin."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.telemetry import get_tracer
from app.models.opportunity import Opportunity


def list_opportunities(db: Session, limit: int, offset: int) -> tuple[list[Opportunity], int]:
    total = db.scalar(select(func.count()).select_from(Opportunity)) or 0

    items = (
        db.execute(
            select(Opportunity)
            .options(selectinload(Opportunity.organization))  # avoid N+1 on organization_name
            .order_by(Opportunity.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .all()
    )

    return list(items), total


def search_opportunities(
    db: Session, query_embedding: list[float], limit: int
) -> list[tuple[Opportunity, float]]:
    """Nearest opportunities to a query vector by pgvector cosine distance."""
    with get_tracer().start_as_current_span("opportunities.search") as span:
        span.set_attribute("search.limit", limit)

        distance = Opportunity.embedding.cosine_distance(query_embedding)

        rows = db.execute(
            select(Opportunity, distance.label("distance"))
            .options(selectinload(Opportunity.organization))
            .where(Opportunity.embedding.is_not(None))
            .order_by(distance)
            .limit(limit)
        ).all()

        span.set_attribute("result.count", len(rows))

    # Similarity (higher = closer) reads better to API consumers than distance.
    return [(opportunity, 1 - dist) for opportunity, dist in rows]
