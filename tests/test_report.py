import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from resumematch.matcher import analyze
from resumematch.report import build_csv, build_text_report
from resumematch.suggestions import generate_suggestions

JD = "Requirements:\n- Java\n- React\n- SQL\nNice to have:\n- Docker"
RESUME = "Java and SQL projects, also Python"


def test_suggestions_cover_missing_required_without_inventing():
    tips = " ".join(generate_suggestions(analyze(RESUME, JD)))
    assert "React" in tips
    assert "Docker" in tips                      # listed as a preferred gap
    assert "if you have" in tips.lower()          # conditional wording, never "add React" outright
    assert "interview" in tips                    # honesty reminder always present


def test_suggestions_skip_matched_skills():
    tips = generate_suggestions(analyze(RESUME, JD))
    assert not any(t.startswith("Add") and "Java" in t for t in tips)


def test_no_score_gives_helpful_message():
    tips = generate_suggestions(analyze(RESUME, "We value kindness."))
    assert len(tips) == 1 and "job description" in tips[0]


def test_csv_has_header_and_rows():
    lines = build_csv(analyze(RESUME, JD)).strip().splitlines()
    assert lines[0] == "skill,category,importance,status,evidence"
    assert len(lines) == 1 + 4


def test_text_report_contents():
    text = build_text_report(analyze(RESUME, JD), today=date(2026, 1, 2))
    assert "Date: 2026-01-02" in text
    assert "Keyword match score:" in text
    assert "MATCHING SKILLS" in text and "SKILLS TO REVIEW" in text
    assert "does not measure experience" in text


def test_text_report_without_score():
    assert "No score" in build_text_report(analyze(RESUME, "We value kindness."))
