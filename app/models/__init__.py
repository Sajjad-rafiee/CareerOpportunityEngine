"""
Import هر دو مدل اینجا لازمه تا SQLAlchemy بتونه رابطه‌ی بین
Organization و Opportunity رو resolve کنه (چون در کد خود مدل‌ها،
ارجاع به مدل دیگه به‌صورت رشته نوشته شده، نه import مستقیم، تا
import چرخه‌ای پیش نیاد).
"""

from app.models.opportunity import Opportunity
from app.models.organization import Organization

__all__ = ["Opportunity", "Organization"]
