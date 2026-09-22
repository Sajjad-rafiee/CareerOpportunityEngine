"""Reads data/opportunities_greenhouse.json and loads it into Postgres.

Idempotent: reruns update existing rows instead of duplicating them,
matched on (source, external_id).

Run: uv run python -m scripts.load_greenhouse_to_db
"""

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.models import Eligibility, Opportunity, Organization
from app.services.eligibility import extract_eligibility
from app.services.embeddings import build_embedding_text, embed_text

logger = logging.getLogger(__name__)

INPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "opportunities_greenhouse.json"


def get_or_create_organization(db: Session, name: str) -> Organization:
    organization = db.query(Organization).filter_by(name=name).first()
    if organization is not None:
        return organization

    organization = Organization(name=name)
    db.add(organization)
    db.flush()
    return organization


def upsert_opportunity(db: Session, record: dict, organization: Organization) -> Opportunity:
    existing = (
        db.query(Opportunity)
        .filter_by(source=record["source"], external_id=record["external_id"])
        .first()
    )

    embedding = embed_text(build_embedding_text(record["title"], record["description"]))

    if existing is not None:
        existing.title = record["title"]
        existing.description = record["description"]
        existing.deadline = record["deadline"]
        existing.posted_at = record["posted_at"]
        existing.embedding = embedding
        return existing

    opportunity = Opportunity(
        organization_id=organization.id,
        title=record["title"],
        description=record["description"],
        type=record["type"],
        url=record["url"],
        deadline=record["deadline"],
        posted_at=record["posted_at"],
        external_id=record["external_id"],
        source=record["source"],
        embedding=embedding,
    )
    db.add(opportunity)
    db.flush()  # need opportunity.id for the Eligibility FK
    return opportunity


def ensure_eligibility(db: Session, opportunity: Opportunity, record: dict) -> None:
    """Extracts once per opportunity. Unlike embeddings (free, local),
    this hits a paid API, so reruns must not re-bill existing rows."""
    if opportunity.eligibility is not None:
        return

    text = build_embedding_text(record["title"], record["description"])
    extraction = extract_eligibility(text)

    db.add(
        Eligibility(
            opportunity_id=opportunity.id,
            offers_visa_sponsorship=extraction.offers_visa_sponsorship,
            german_language_required=extraction.german_language_required,
            experience_level=extraction.experience_level,
            remote_friendly=extraction.remote_friendly,
        )
    )


def main() -> None:
    setup_logging()

    records = json.loads(INPUT_PATH.read_text())

    with SessionLocal() as db:
        organizations_by_name: dict[str, Organization] = {}

        for record in records:
            org_name = record["organization_name"]
            if org_name not in organizations_by_name:
                organizations_by_name[org_name] = get_or_create_organization(db, org_name)

            opportunity = upsert_opportunity(db, record, organizations_by_name[org_name])
            ensure_eligibility(db, opportunity, record)

        db.commit()

    logger.info("Loaded %d opportunities from %s into the database", len(records), INPUT_PATH)


if __name__ == "__main__":
    main()
