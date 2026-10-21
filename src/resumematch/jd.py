"""Parse a job description into required vs. preferred skills."""
from __future__ import annotations

import re

from .normalize import normalize_text
from .skills import find_skills, load_skills

REQUIRED = "Required"
PREFERRED = "Preferred"

# Phrases that mark a clause (or a whole section) as optional.
_PREFERRED_CUES = [
    "preferred", "nice to have", "nice-to-have", "good to have", "bonus",
    "desirable", "a plus", "is a plus", "are a plus", "optional", "ideally",
    "not required", "would be a plus", "extra credit",
]
# Headers that switch back to required.
_REQUIRED_HEADERS = [
    "requirements", "required", "qualifications", "minimum qualifications",
    "must have", "must-have", "what you need", "what you'll need", "you have",
    "responsibilities", "what you will do", "what you'll do",
]

_cue_alt = "|".join(re.escape(c) for c in _PREFERRED_CUES)
_req_alt = "|".join(re.escape(h) for h in _REQUIRED_HEADERS)

_PREFERRED_ANYWHERE = re.compile(rf"(?<![a-z])({_cue_alt})(?![a-z])")
# A header looks like "nice to have:" / "preferred qualifications:" at the start of a line.
_PREFERRED_HEADER = re.compile(rf"^({_cue_alt})\b[^:\n]{{0,25}}:")
_REQUIRED_HEADER = re.compile(rf"^({_req_alt})\b[^:\n]{{0,25}}:")
# Split into clauses on ';' and sentence-ending periods (not the dot in "node.js").
_CLAUSE_SPLIT = re.compile(r";|\.(?=\s|$)")


def classify_job_skills(jd_text: str, skills: dict[str, dict] | None = None,
                        include_soft_skills: bool = False) -> dict[str, dict]:
    """Return {skill: {"category": ..., "importance": "Required" | "Preferred"}}.

    Rules (deliberately simple and explainable):
      1. Everything is Required by default.
      2. A header like "Nice to have:" makes the following lines Preferred
         until a Required-style header (e.g. "Requirements:") appears.
      3. A clause containing a cue like "a plus" or "bonus" is Preferred.
      4. If a skill is mentioned as both, Required wins.
    """
    skills = skills if skills is not None else load_skills()
    result: dict[str, dict] = {}
    section = REQUIRED

    for line in normalize_text(jd_text).split("\n"):
        line = line.strip()
        if not line:
            continue
        if _REQUIRED_HEADER.match(line):
            section = REQUIRED
        elif _PREFERRED_HEADER.match(line):
            section = PREFERRED

        for clause in _CLAUSE_SPLIT.split(line):
            importance = PREFERRED if (section == PREFERRED or _PREFERRED_ANYWHERE.search(clause)) else REQUIRED
            for name, match in find_skills(clause, skills).items():
                if not include_soft_skills and match.category == "Soft skill":
                    continue
                existing = result.get(name)
                if existing is None or (existing["importance"] == PREFERRED and importance == REQUIRED):
                    result[name] = {"category": match.category, "importance": importance}
    return result
