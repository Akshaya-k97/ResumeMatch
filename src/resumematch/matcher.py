"""Compare resume skills against job-description skills and compute a transparent score."""
from __future__ import annotations

from dataclasses import dataclass, field

from .jd import PREFERRED, REQUIRED, classify_job_skills
from .normalize import normalize_text
from .skills import find_skills, load_skills

# Scoring weights. Shown in the UI so the score is never a black box.
WEIGHTS = {REQUIRED: 2, PREFERRED: 1}

MATCHED = "Matched"
MISSING = "Missing"


@dataclass
class SkillRow:
    skill: str
    category: str
    importance: str
    status: str
    evidence: str = ""   # snippet from the resume (matched skills only)


@dataclass
class AnalysisResult:
    rows: list[SkillRow]
    score: int | None                 # None when the job description has no recognized skills
    required_matched: int = 0
    required_total: int = 0
    preferred_matched: int = 0
    preferred_total: int = 0
    extra_resume_skills: list[str] = field(default_factory=list)  # in resume, not in job description
    warnings: list[str] = field(default_factory=list)

    @property
    def matched(self) -> list[SkillRow]:
        return [r for r in self.rows if r.status == MATCHED]

    @property
    def missing(self) -> list[SkillRow]:
        return [r for r in self.rows if r.status == MISSING]

    def to_dataframe(self):
        import pandas as pd
        cols = ["skill", "category", "importance", "status", "evidence"]
        return pd.DataFrame([vars(r) for r in self.rows], columns=cols)


def analyze(resume_text: str, jd_text: str, skills: dict[str, dict] | None = None,
            include_soft_skills: bool = False) -> AnalysisResult:
    skills = skills if skills is not None else load_skills()

    job = classify_job_skills(jd_text, skills, include_soft_skills)
    resume = find_skills(normalize_text(resume_text), skills)

    warnings: list[str] = []
    if not job:
        warnings.append("No known skills were found in the job description, so no score can be calculated.")

    rows: list[SkillRow] = []
    for name, info in job.items():
        hit = resume.get(name)
        rows.append(SkillRow(
            skill=name,
            category=info["category"],
            importance=info["importance"],
            status=MATCHED if hit else MISSING,
            evidence=hit.snippet if hit else "",
        ))
    # Required first, then matched first, then alphabetical: stable, readable ordering.
    rows.sort(key=lambda r: (r.importance != REQUIRED, r.status != MATCHED, r.skill.lower()))

    def count(importance: str, status: str | None = None) -> int:
        return sum(1 for r in rows if r.importance == importance and (status is None or r.status == status))

    total_weight = sum(WEIGHTS[r.importance] for r in rows)
    got_weight = sum(WEIGHTS[r.importance] for r in rows if r.status == MATCHED)
    score = round(100 * got_weight / total_weight) if total_weight else None

    extras = sorted(n for n in resume if n not in job and (include_soft_skills or resume[n].category != "Soft skill"))

    return AnalysisResult(
        rows=rows,
        score=score,
        required_matched=count(REQUIRED, MATCHED),
        required_total=count(REQUIRED),
        preferred_matched=count(PREFERRED, MATCHED),
        preferred_total=count(PREFERRED),
        extra_resume_skills=extras,
        warnings=warnings,
    )
