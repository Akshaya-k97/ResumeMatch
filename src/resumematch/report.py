"""Build downloadable reports (CSV and plain text)."""
from __future__ import annotations

from datetime import date

from .matcher import WEIGHTS, AnalysisResult
from .suggestions import generate_suggestions


def build_csv(result: AnalysisResult) -> str:
    return result.to_dataframe().to_csv(index=False)


def build_text_report(result: AnalysisResult, today: date | None = None) -> str:
    today = today or date.today()
    lines = ["RESUMEMATCH ANALYSIS REPORT", f"Date: {today.isoformat()}", ""]

    if result.score is None:
        lines += ["No score: no known skills were found in the job description.", ""]
    else:
        lines += [
            f"Keyword match score: {result.score}%",
            f"  Required skills:  {result.required_matched}/{result.required_total} matched",
            f"  Preferred skills: {result.preferred_matched}/{result.preferred_total} matched",
            f"  Weights: required x{WEIGHTS['Required']}, preferred x{WEIGHTS['Preferred']}",
            "",
            "Note: this score is the weighted share of detected job keywords found in the resume.",
            "It does not measure experience level, seniority, or overall fit.",
            "",
        ]

    lines.append("MATCHING SKILLS")
    lines += [f"  - {r.skill} ({r.importance})" for r in result.matched] or ["  (none)"]
    lines += ["", "SKILLS TO REVIEW"]
    lines += [f"  - {r.skill} ({r.importance})" for r in result.missing] or ["  (none)"]

    if result.extra_resume_skills:
        lines += ["", "ON YOUR RESUME BUT NOT IN THIS JOB DESCRIPTION", "  " + ", ".join(result.extra_resume_skills)]

    lines += ["", "SUGGESTIONS"]
    lines += [f"  - {s}" for s in generate_suggestions(result)]
    return "\n".join(lines) + "\n"
