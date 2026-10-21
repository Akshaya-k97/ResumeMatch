import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from resumematch.matcher import MATCHED, MISSING, RELATED, analyze
from resumematch.report import build_text_report
from resumematch.similarity import text_similarity
from resumematch.suggestions import generate_suggestions


def test_related_skill_gets_half_credit():
    r = analyze("Built a MySQL database", "Requirements:\n- SQL")
    assert [(x.skill, x.status, x.evidence) for x in r.rows] == [("SQL", RELATED, "via MySQL")]
    assert r.score == 50


def test_exact_beats_related_and_missing_is_zero():
    assert analyze("SQL queries", "SQL").score == 100
    assert analyze("gardening", "SQL").score == 0


def test_related_can_be_disabled():
    r = analyze("Built a MySQL database", "SQL", use_related=False)
    assert r.rows[0].status == MISSING and r.score == 0


def test_related_is_not_transitive_or_one_way_surprising():
    # JavaScript experience should NOT count as React experience
    assert analyze("JavaScript projects", "React").rows[0].status == MISSING


def test_counts_include_related():
    r = analyze("MySQL and Java", "Requirements:\n- SQL\n- Java\nNice to have:\n- Docker")
    assert (r.required_matched, r.required_related, r.required_total) == (1, 1, 2)
    assert r.preferred_related == 0 and r.preferred_total == 1


def test_suggestion_and_report_mention_related():
    r = analyze("MySQL", "SQL")
    assert any("related" in t and "SQL" in t for t in generate_suggestions(r))
    assert "RELATED SKILLS" in build_text_report(r)


def test_text_similarity_range_and_ordering():
    jd = "We need a Python developer with Flask and SQL experience building APIs"
    close = "Python developer who built Flask APIs with SQL databases"
    far = "Experienced pastry chef specializing in sourdough bread and cakes"
    s_close, s_far = text_similarity(close, jd), text_similarity(far, jd)
    assert 0 <= s_far < s_close <= 100


def test_text_similarity_handles_empty():
    assert text_similarity("", "anything") is None
