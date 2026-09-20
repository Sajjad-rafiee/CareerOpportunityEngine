"""
Engine و Session factory برای اتصال به Postgres.

عمداً engine رو موقع import ساخته نمی‌شه (lazy، پشت get_engine())، چون
اگه ساخته بشه یعنی صرفاً import کردن این فایل، بدون اینکه واقعاً بخوایم
به دیتابیس وصل بشیم، تنظیمات .env رو لازم داره. این باعث می‌شه مثلاً
در CI که .env وجود نداره، تست‌هایی که اصلاً کاری به دیتابیس واقعی
ندارن (و به‌جاش SQLite در حافظه استفاده می‌کنن) هم fail بشن.
"""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url)


def SessionLocal() -> Session:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)()


def get_db() -> Generator[Session, None, None]:
    """برای استفاده به‌عنوان FastAPI dependency در فازهای بعدی (endpoint ها)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
