"""get_or_create_organization / upsert_opportunity logic against SQLite,
not real Postgres. embed_text is mocked so these stay fast."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import scripts.load_greenhouse_to_db as loader
from app.db.base import Base
from app.models import Opportunity, Organization
from scripts.load_greenhouse_to_db import get_or_create_organization, upsert_opportunity


@pytest.fixture
def db(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(loader, "embed_text", lambda text: [0.0] * 384)

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def make_record(**overrides) -> dict:
    record = {
        "title": "AI Engineer",
        "description": "desc",
        "type": "job",
        "url": "https://example.com/jobs/1",
        "deadline": None,
        "posted_at": None,
        "organization_name": "N26",
        "external_id": "1",
        "source": "greenhouse",
    }
    record.update(overrides)
    return record


def test_get_or_create_organization_reuses_existing_row(db):
    first = get_or_create_organization(db, "N26")
    second = get_or_create_organization(db, "N26")

    assert first.id == second.id
    assert db.query(Organization).count() == 1


def test_upsert_opportunity_inserts_new_record(db):
    organization = get_or_create_organization(db, "N26")

    upsert_opportunity(db, make_record(), organization)
    db.commit()

    saved = db.query(Opportunity).one()
    assert saved.title == "AI Engineer"
    assert saved.organization_id == organization.id


def test_upsert_opportunity_updates_instead_of_duplicating(db):
    organization = get_or_create_organization(db, "N26")
    upsert_opportunity(db, make_record(), organization)
    db.commit()

    upsert_opportunity(db, make_record(title="Senior AI Engineer"), organization)
    db.commit()

    assert db.query(Opportunity).count() == 1
    assert db.query(Opportunity).one().title == "Senior AI Engineer"
