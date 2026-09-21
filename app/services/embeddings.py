"""
تبدیل متن آگهی به بردار عددی (embedding) برای جستجوی معنایی.

مدل: sentence-transformers/all-MiniLM-L6-v2 — کوچیک، رایگان، کاملاً
لوکال (بدون نیاز به API key یا اینترنت بعد از اولین دانلود مدل).
"""

import html
import re
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.models.opportunity import EMBEDDING_DIMENSIONS

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_TAG_RE = re.compile(r"<[^>]+>")


def clean_html(raw: str) -> str:
    """
    Greenhouse توضیحات رو به‌صورت HTML با entity های escape‌شده برمی‌گردونه
    (مثلاً &lt;p&gt; به‌جای <p>). برای embedding فقط متن ساده لازمه، وگرنه
    خود تگ‌ها نویز بی‌معنی به بردار اضافه می‌کنن.
    """
    return _TAG_RE.sub(" ", html.unescape(raw))


def build_embedding_text(title: str, description: str | None) -> str:
    """
    تصمیم: عنوان + توضیحات تمیزشده با هم embed می‌شن.

    فقط عنوان: خیلی کوتاهه، جزئیات مهم (نیازمندی‌ها، مهارت‌ها) رو نداره.
    فقط توضیحات: عنوان معمولاً قوی‌ترین سیگنال معناییه، از دستش ندیم.
    """
    parts = [title]
    if description:
        parts.append(clean_html(description))
    return " ".join(parts)


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    """مدل فقط یک‌بار از دیسک/دانلود لود می‌شه، نه هر بار که embed_text صدا زده بشه."""
    return SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    # normalize_embeddings=True یعنی بردارها طول واحد دارن، پس فاصله‌ی
    # کسینوسی همون ضرب داخلی ساده می‌شه — استاندارد برای جستجوی شباهت.
    vector = get_embedding_model().encode(text, normalize_embeddings=True, show_progress_bar=False)
    embedding = vector.tolist()
    assert len(embedding) == EMBEDDING_DIMENSIONS
    return embedding
