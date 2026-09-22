"""
تنظیم متمرکز logging برای کل پروژه.

فقط یک تابع دارد که باید یک‌بار، در نقطه‌ی ورود هر بخش قابل‌اجرا
(FastAPI app، یا یک اسکریپت) صدا زده شود. بعد از آن، هر ماژول با
``logging.getLogger(__name__)`` لاگر خودش را می‌گیرد — نیازی نیست
هیچ جای دیگری این تنظیمات تکرار شود.
"""

import logging
import os

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = logging.getLevelNamesMapping().get(level_name, logging.INFO)

    logging.basicConfig(level=level, format=LOG_FORMAT)

    # کتابخونه‌های شخص ثالث (httpx و غیره) در سطح INFO خیلی پرحرفن؛
    # مگر این‌که صریحاً DEBUG بخوایم، سطحشون رو بالاتر می‌بریم.
    if level > logging.DEBUG:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        # یک warning یک‌باره‌ی خود SDK درباره‌ی الگوی داخلیش (AFC) - به ما
        # ربطی نداره، فقط نویزه.
        logging.getLogger("google_genai.models").setLevel(logging.ERROR)
