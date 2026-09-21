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


def search_opportunities(
    db: Session, query_embedding: list[float], limit: int
) -> list[tuple[Opportunity, float]]:
    """
    نزدیک‌ترین آگهی‌ها به یک بردار query، بر اساس فاصله‌ی کسینوسی pgvector.

    رکوردهایی که هنوز embedding ندارن (مثلاً چون قبل از این migration
    وارد شدن) رد می‌شن، چون فاصله‌شون بی‌معنیه.
    """
    distance = Opportunity.embedding.cosine_distance(query_embedding)

    rows = db.execute(
        select(Opportunity, distance.label("distance"))
        .options(selectinload(Opportunity.organization))
        .where(Opportunity.embedding.is_not(None))
        .order_by(distance)
        .limit(limit)
    ).all()

    # cosine_distance = 1 - cosine_similarity، پس similarity رو برمی‌گردونیم
    # چون برای کاربر عدد «شباهت» (بزرگ‌تر = بهتر) قابل‌فهم‌تر از «فاصله»‌ست.
    return [(opportunity, 1 - dist) for opportunity, dist in rows]
