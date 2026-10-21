"""Supplementary signal: TF-IDF cosine similarity between whole documents."""
from __future__ import annotations


def text_similarity(resume_text: str, jd_text: str) -> int | None:
    """Return 0-100 similarity of the two texts, or None if scikit-learn is unavailable/inputs empty.

    This is a rough, supplementary signal: it rewards shared vocabulary (including
    non-dictionary terms) but cannot tell required from optional or understand meaning.
    """
    if not resume_text.strip() or not jd_text.strip():
        return None
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        return None

    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True,
                          token_pattern=r"(?u)\b[\w+#.]*\w[\w+#]*\b")
    try:
        matrix = vec.fit_transform([resume_text.lower(), jd_text.lower()])
    except ValueError:  # empty vocabulary after stop-word removal
        return None
    return round(100 * float(cosine_similarity(matrix[0], matrix[1])[0, 0]))
