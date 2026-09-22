import uuid
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.eligibility import Eligibility
    from app.models.organization import Organization

# ابعاد بردار sentence-transformers/all-MiniLM-L6-v2. اگه مدل embedding
# عوض بشه، این عدد هم باید عوض بشه (و یک migration جدید بخواد).
EMBEDDING_DIMENSIONS = 384


class Opportunity(Base):
    __tablename__ = "opportunities"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_opportunity_source_external_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"))

    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    type: Mapped[str] = mapped_column(String(50))
    url: Mapped[str] = mapped_column(Text, unique=True)
    deadline: Mapped[date | None] = mapped_column(Date, default=None)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    external_id: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(50))

    # nullable چون رکوردهایی که قبل از این migration وارد شدن، یا رکوردهایی
    # که مدل embedding موقع لود کردنشون در دسترس نبوده، بردار ندارن.
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIMENSIONS), default=None
    )

    organization: Mapped["Organization"] = relationship(back_populates="opportunities")
    eligibility: Mapped["Eligibility | None"] = relationship(
        back_populates="opportunity", uselist=False
    )

    @property
    def organization_name(self) -> str:
        """
        برای این‌که OpportunityResponse بتونه با from_attributes خودکار
        این مقدار رو از روی رابطه organization بگیره، بدون این‌که لایه‌ی
        API مجبور باشه دستی این مپینگ رو انجام بده.
        """
        return self.organization.name
