import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity


class Organization(Base):
    """
    نسخه‌ی حداقلی: فقط ستون‌هایی که در این مرحله واقعاً داده براشون داریم.

    ERD کامل‌تر (type, country, city, website) وقتی اضافه می‌شه که یک
    منبع دوم یا فرآیند غنی‌سازی داده، واقعاً این اطلاعات رو تامین کنه.
    """

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), unique=True)

    opportunities: Mapped[list["Opportunity"]] = relationship(back_populates="organization")
