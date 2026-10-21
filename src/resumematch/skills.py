"""Skill dictionary loading and alias-based skill detection."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SKILLS_PATH = Path(__file__).resolve().parents[2] / "data" / "skills.json"

# A skill alias must not be glued to other letters, digits, '+' or '#'.
# This keeps "java" from matching inside "javascript" and "c" out of "c++".
_LEFT = r"(?<![A-Za-z0-9+#])"
_RIGHT = r"(?![A-Za-z0-9+#])"


@dataclass(frozen=True)
class SkillMatch:
    skill: str
    category: str
    alias: str      # the alias that triggered the match
    snippet: str    # surrounding text, as evidence


def load_skills(path: str | Path = DEFAULT_SKILLS_PATH) -> dict[str, dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _alias_pattern(alias: str) -> re.Pattern:
    escaped = re.escape(alias.lower()).replace(r"\ ", r"\s+")
    return re.compile(_LEFT + escaped + _RIGHT)


def build_matchers(skills: dict[str, dict]) -> list[tuple[str, str, str, re.Pattern]]:
    matchers = []
    for name, info in skills.items():
        for alias in info["aliases"]:
            matchers.append((name, info["category"], alias, _alias_pattern(alias)))
    return matchers


def find_skills(normalized_text: str, skills: dict[str, dict] | None = None,
                snippet_chars: int = 40) -> dict[str, SkillMatch]:
    """Return {canonical skill: first SkillMatch}. Input must already be normalized."""
    skills = skills if skills is not None else load_skills()
    found: dict[str, SkillMatch] = {}
    for name, category, alias, pattern in build_matchers(skills):
        if name in found:
            continue
        m = pattern.search(normalized_text)
        if m:
            start = max(0, m.start() - snippet_chars)
            end = min(len(normalized_text), m.end() + snippet_chars)
            snippet = " ".join(normalized_text[start:end].split())
            found[name] = SkillMatch(name, category, alias, snippet)
    return found
