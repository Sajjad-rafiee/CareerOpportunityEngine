"""
کلاس پایه‌ای که همه‌ی مدل‌های SQLAlchemy باید از آن ارث‌بری کنند.

جدا نگه‌داشتنش از session.py عمدیه: Alembic برای autogenerate به
Base.metadata نیاز داره، بدون این‌که لازم باشه engine واقعی رو import کنه.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
