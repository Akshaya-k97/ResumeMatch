"""Clean raw extracted text so skill matching behaves predictably."""
from __future__ import annotations

import re
import unicodedata

_BULLETS = "•●▪■◦○➢➤✓✔►–—"  # bullets and dashes that PDFs love to emit
_DASH_TRANSLATION = {ord(c): " " for c in _BULLETS}


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00ad", "")                     # soft hyphens
    text = re.sub(r"(\w)-\n(?=[a-z])", r"\1", text)       # re-join words hyphenated across lines
    text = text.translate(_DASH_TRANSLATION)
    text = text.lower()
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()
