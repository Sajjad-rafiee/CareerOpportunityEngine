"""Pure-function tests for app.services.embeddings; no model loading."""

from app.services.embeddings import build_embedding_text, clean_html


def test_clean_html_removes_tags_and_unescapes_entities():
    raw = "&lt;p&gt;Hello &amp; welcome&lt;/p&gt;"

    result = clean_html(raw)

    assert "<" not in result
    assert ">" not in result
    assert "Hello & welcome" in result


def test_build_embedding_text_combines_title_and_cleaned_description():
    text = build_embedding_text("AI Engineer", "&lt;p&gt;Build models&lt;/p&gt;")

    assert text.startswith("AI Engineer")
    assert "Build models" in text
    assert "<p>" not in text


def test_build_embedding_text_handles_missing_description():
    text = build_embedding_text("AI Engineer", None)

    assert text == "AI Engineer"
