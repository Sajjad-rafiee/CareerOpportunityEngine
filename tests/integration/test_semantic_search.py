"""
تست integration: مدل embedding واقعی رو لود می‌کنه (دانلود وزن‌ها در
اولین اجرا) و چک می‌کنه که دو متن هم‌معنی، حتی بدون کلمه‌ی مشترک،
شباهت بیشتری نسبت به یک متن کاملاً بی‌ربط دارن — دقیقاً همون تست
موفقیتی که برای این فاز لازم داریم.
"""

import pytest

from app.services.embeddings import embed_text

pytestmark = pytest.mark.integration


def test_semantically_related_text_is_closer_than_unrelated_text_with_no_shared_words():
    backend_job = embed_text("We are hiring a backend engineer with Python experience")
    similar_job = embed_text("Looking for a software developer skilled in server-side coding")
    unrelated_text = embed_text("Fresh croissants baked every morning in our bakery")

    # embed_text با normalize_embeddings=True برمی‌گردونه، پس ضرب داخلی
    # همون شباهت کسینوسیه.
    similarity_to_similar_job = sum(x * y for x, y in zip(backend_job, similar_job, strict=True))
    similarity_to_unrelated = sum(x * y for x, y in zip(backend_job, unrelated_text, strict=True))

    assert similarity_to_similar_job > similarity_to_unrelated
