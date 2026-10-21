import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from resumematch.normalize import normalize_text
from resumematch.skills import find_skills


def detect(text: str) -> set[str]:
    return set(find_skills(normalize_text(text)))


def test_java_is_not_javascript():
    assert detect("Built apps in JavaScript") == {"JavaScript"}
    assert detect("Built apps in Java") == {"Java"}


def test_aliases_map_to_one_skill():
    assert "React" in detect("Experience with React.js")
    assert "React" in detect("Experience with ReactJS")
    assert "REST APIs" in detect("Designed RESTful services")


def test_symbol_skills():
    assert "C++" in detect("Proficient in C++ and Python")
    assert "C#" in detect("Wrote C# services")
    assert ".NET" in detect("ASP.NET Core backend")


def test_git_vs_github():
    assert detect("Used Git for version control") == {"Git"}
    assert detect("Hosted on GitHub") == {"GitHub"}


def test_sql_not_inside_mysql():
    assert detect("Worked with MySQL") == {"MySQL"}


def test_word_boundaries_avoid_false_positives():
    # "go" is only matched via "golang", so the verb is safe
    assert detect("I will go to the gym") == set()
    # skills glued to other letters are not matched
    assert detect("scripting with javascripty things") == set()


# Known limitation (documented for the README): "react" the verb still matches React,
# because the dictionary has no context rules yet. Phase 2/4 can address this.


def test_multiline_alias_and_bullets():
    text = "• Data\nStructures and Algorithms\n• Object-oriented design"
    assert {"Data Structures & Algorithms", "OOP"} <= detect(text)


def test_hyphenated_line_break_rejoined():
    assert normalize_text("develop-\nment") == "development"
