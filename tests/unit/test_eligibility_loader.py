"""ensure_eligibility logic against SQLite, with extract_eligibility
mocked - no real Gemini or Postgres."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import scripts.load_greenhouse_to_db as loader
from app.db.base import Base
from app.models import Eligibility, Opportunity, Organization
from app.services.eligibility import EligibilityExtraction


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def make_opportunity(db: Session, organization: Organization) -> Opportunity:
    opportunity = Opportunity(
        organization_id=organization.id,
        title="AI Engineer",
        type="job",
        url="https://example.com/1",
        external_id="1",
        source="greenhouse",
    )
    db.add(opportunity)
    db.flush()
    return opportunity


def test_ensure_eligibility_creates_record_when_missing(
    monkeypatch: pytest.MonkeyPatch, db: Session
):
    monkeypatch.setattr(
        loader,
        "extract_eligibility",
        lambda text: EligibilityExtraction(
            offers_visa_sponsorship=True,
            german_language_required=False,
            experience_level="mid",
            remote_friendly=True,
        ),
    )

    organization = Organization(name="N26")
    db.add(organization)
    db.flush()
    opportunity = make_opportunity(db, organization)

    loader.ensure_eligibility(db, opportunity, {"title": "AI Engineer", "description": None})
    db.commit()

    saved = db.query(Eligibility).one()
    assert saved.offers_visa_sponsorship is True
    assert saved.experience_level == "mid"


def test_ensure_eligibility_skips_when_already_present(
    monkeypatch: pytest.MonkeyPatch, db: Session
):
    calls = {"count": 0}

    def fake_extract(text: str) -> EligibilityExtraction:
        calls["count"] += 1
        return EligibilityExtraction(experience_level="mid")

    monkeypatch.setattr(loader, "extract_eligibility", fake_extract)

    organization = Organization(name="N26")
    db.add(organization)
    db.flush()
    opportunity = make_opportunity(db, organization)
    record = {"title": "AI Engineer", "description": None}

    loader.ensure_eligibility(db, opportunity, record)
    db.commit()
    assert calls["count"] == 1

    # Second call on the same opportunity: should not hit Gemini again.
    loader.ensure_eligibility(db, opportunity, record)
    db.commit()
    assert calls["count"] == 1
    assert db.query(Eligibility).count() == 1
