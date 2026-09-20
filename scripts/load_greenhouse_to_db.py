"""
داده‌ی normalize‌شده‌ی data/opportunities_greenhouse.json (خروجی
scripts/fetch_greenhouse.py) رو می‌خونه و توی Postgres می‌ریزه.

Idempotent: اگه دوباره اجرا بشه، رکوردهای تکراری نمی‌سازه — به‌جاش
رکورد موجود رو آپدیت می‌کنه. یکتایی از روی (source, external_id) چک
می‌شه، چون همون چیزیه که در سطح دیتابیس هم constraint داره.
"""

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.models import Opportunity, Organization

logger = logging.getLogger(__name__)

INPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "opportunities_greenhouse.json"


def get_or_create_organization(db: Session, name: str) -> Organization:
    organization = db.query(Organization).filter_by(name=name).first()
    if organization is not None:
        return organization

    organization = Organization(name=name)
    db.add(organization)
    db.flush()  # UUID رو بدون commit کردن کل transaction می‌گیریم
    return organization


def upsert_opportunity(db: Session, record: dict, organization: Organization) -> None:
    existing = (
        db.query(Opportunity)
        .filter_by(source=record["source"], external_id=record["external_id"])
        .first()
    )

    if existing is not None:
        existing.title = record["title"]
        existing.description = record["description"]
        existing.deadline = record["deadline"]
        existing.posted_at = record["posted_at"]
        return

    db.add(
        Opportunity(
            organization_id=organization.id,
            title=record["title"],
            description=record["description"],
            type=record["type"],
            url=record["url"],
            deadline=record["deadline"],
            posted_at=record["posted_at"],
            external_id=record["external_id"],
            source=record["source"],
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

            upsert_opportunity(db, record, organizations_by_name[org_name])

        db.commit()

    logger.info("Loaded %d opportunities from %s into the database", len(records), INPUT_PATH)


if __name__ == "__main__":
    main()
