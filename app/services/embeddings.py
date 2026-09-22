"""Turns posting text into vectors for semantic search.

Model: sentence-transformers/all-MiniLM-L6-v2 - small, free, fully local.
"""

import html
import re
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.models.opportunity import EMBEDDING_DIMENSIONS

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_TAG_RE = re.compile(r"<[^>]+>")


def clean_html(raw: str) -> str:
    """Greenhouse descriptions are HTML with escaped entities; strip both."""
    return _TAG_RE.sub(" ", html.unescape(raw))


def build_embedding_text(title: str, description: str | None) -> str:
    """Title + cleaned description: title alone lacks detail, description
    alone loses the strongest signal."""
    parts = [title]
    if description:
        parts.append(clean_html(description))
    return " ".join(parts)


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    # normalize_embeddings=True: unit-length vectors, so cosine distance
    # reduces to a plain dot product.
    vector = get_embedding_model().encode(text, normalize_embeddings=True, show_progress_bar=False)
    embedding = vector.tolist()
    assert len(embedding) == EMBEDDING_DIMENSIONS
    return embedding
