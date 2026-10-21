import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from resumematch.jd import PREFERRED, REQUIRED, classify_job_skills
from resumematch.matcher import analyze


def imp(jd: str) -> dict[str, str]:
    return {k: v["importance"] for k, v in classify_job_skills(jd).items()}


def test_default_is_required():
    assert imp("We need Java and SQL") == {"Java": REQUIRED, "SQL": REQUIRED}


def test_nice_to_have_section_is_preferred():
    jd = "Requirements:\n- Java\nNice to have:\n- Docker\n- AWS"
    assert imp(jd) == {"Java": REQUIRED, "Docker": PREFERRED, "AWS": PREFERRED}


def test_required_header_resets_section():
    jd = "Nice to have:\n- Docker\nRequirements:\n- Python"
    assert imp(jd) == {"Docker": PREFERRED, "Python": REQUIRED}


def test_inline_cue_only_affects_its_clause():
    assert imp("Java is required; Docker is a plus") == {"Java": REQUIRED, "Docker": PREFERRED}


def test_required_wins_when_mentioned_twice():
    jd = "Nice to have:\n- Git\nRequirements:\n- Git"
    assert imp(jd) == {"Git": REQUIRED}


def test_score_is_weighted_and_transparent():
    jd = "Requirements:\n- Java\n- SQL\nNice to have:\n- Docker"
    # weights: Java 2 + SQL 2 + Docker 1 = 5 total; resume matches Java + Docker = 3
    r = analyze("Java and Docker projects", jd)
    assert r.score == 60
    assert (r.required_matched, r.required_total) == (1, 2)
    assert (r.preferred_matched, r.preferred_total) == (1, 1)
    assert [x.skill for x in r.missing] == ["SQL"]


def test_perfect_and_zero_scores():
    jd = "Java and SQL"
    assert analyze("java sql", jd).score == 100
    assert analyze("I like gardening", jd).score == 0


def test_no_skills_in_jd_gives_no_score():
    r = analyze("Java", "We value curiosity and kindness.")
    assert r.score is None and r.warnings


def test_extra_skills_and_evidence():
    r = analyze("Built apps with Java and Python", "Java required")
    assert r.extra_resume_skills == ["Python"]
    assert "java" in r.matched[0].evidence


def test_soft_skills_excluded_by_default():
    assert "Communication" not in imp("Strong communication and Java")
    assert "Communication" in {k for k in classify_job_skills("Strong communication and Java", include_soft_skills=True)}


def test_dataframe_columns():
    df = analyze("Java", "Java and SQL").to_dataframe()
    assert list(df.columns) == ["skill", "category", "importance", "status", "evidence"]
    assert len(df) == 2
