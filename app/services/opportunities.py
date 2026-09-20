"""
منطق واکشی Opportunity ها از دیتابیس. لایه‌ی API فقط این تابع رو صدا
می‌زنه و نتیجه رو به فرمت پاسخ تبدیل می‌کنه — خودش هیچ کوئری‌ای نمی‌زنه.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.opportunity import Opportunity


def list_opportunities(db: Session, limit: int, offset: int) -> tuple[list[Opportunity], int]:
    total = db.scalar(select(func.count()).select_from(Opportunity)) or 0

    items = (
        db.execute(
            select(Opportunity)
            # بدون این، برای هر رکورد یک کوئری جدا برای گرفتن organization.name
            # زده می‌شد (مشکل معروف N+1). با selectinload، همه‌ی سازمان‌های
            # لازم رو با یک کوئری اضافه‌ی واحد میاره.
            .options(selectinload(Opportunity.organization))
            .order_by(Opportunity.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .all()
    )

    return list(items), total
