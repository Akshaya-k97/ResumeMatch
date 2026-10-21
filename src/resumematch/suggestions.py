"""Rule-based, honest suggestions. Never tells the user to claim skills they don't have."""
from __future__ import annotations

from .jd import REQUIRED
from .matcher import AnalysisResult

MAX_SKILL_TIPS = 5

_CATEGORY_TIPS = {
    "Language":  "Add a project or experience bullet showing your use of {skill}, if you have it.",
    "Framework": "Add relevant project experience demonstrating {skill}, if you have it.",
    "Concept":   "Mention {skill} work if you've actually done it (for example in a project or coursework).",
    "Database":  "If you've queried or designed with {skill}, name it in a project bullet.",
    "Cloud":     "If you've deployed or used {skill} (even a small project), say so with what you built.",
    "Tool":      "If you've used {skill}, list it where it fits, such as a project or skills section.",
    "Practice":  "If you've worked this way ({skill}), mention it in a team project or internship bullet.",
    "Data":      "If you've used {skill} in coursework or projects, name the project and what you did.",
    "Web":       "If you've built with {skill}, mention the page or project.",
}
_DEFAULT_TIP = "If you have experience with {skill}, make sure it appears in your resume."


def generate_suggestions(result: AnalysisResult) -> list[str]:
    if result.score is None:
        return ["Paste a job description that lists specific technical skills so the analysis has something to compare."]

    tips: list[str] = []

    missing_required = [r for r in result.missing if r.importance == REQUIRED]
    for row in missing_required[:MAX_SKILL_TIPS]:
        tips.append(_CATEGORY_TIPS.get(row.category, _DEFAULT_TIP).format(skill=row.skill))
    if len(missing_required) > MAX_SKILL_TIPS:
        tips.append(f"{len(missing_required) - MAX_SKILL_TIPS} more required skills were not found; review the table.")

    missing_preferred = [r.skill for r in result.missing if r.importance != REQUIRED]
    if missing_preferred:
        tips.append("Preferred (nice-to-have) skills not found: " + ", ".join(missing_preferred)
                    + ". These matter less; add them only if you have real experience.")

    if result.score >= 80:
        tips.append("Strong keyword overlap. Spend your effort on quantifying impact in your project and experience bullets.")
    elif result.score < 40 and result.required_total:
        tips.append("Few required skills matched. Consider whether this role fits your current skills, "
                    "or build a small project that uses the missing ones.")

    if result.extra_resume_skills:
        tips.append("Your resume also lists skills this posting doesn't mention ("
                    + ", ".join(result.extra_resume_skills[:8])
                    + "). Keep what is relevant, but lead with what the role asks for.")

    tips.append("Highlight projects and experience that match the role, and only claim skills you could discuss in an interview.")
    return tips
