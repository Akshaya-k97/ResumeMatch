"""Phase 1 demo: extract text from a PDF (or read a .txt) and list detected skills.

Usage:
    python run_phase1.py path/to/resume.pdf
    python run_phase1.py path/to/job_description.txt
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from resumematch.extract import extract_text_from_pdf
from resumematch.normalize import normalize_text
from resumematch.skills import find_skills


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])

    if path.suffix.lower() == ".pdf":
        result = extract_text_from_pdf(path)
        raw, warnings = result.text, result.warnings
        print(f"Pages: {result.pages}")
    else:
        raw, warnings = path.read_text(encoding="utf-8"), []

    for w in warnings:
        print(f"WARNING: {w}")

    text = normalize_text(raw)
    print(f"Characters after cleaning: {len(text)}\n")
    print("--- First 500 characters ---")
    print(text[:500], "\n")

    found = find_skills(text)
    print(f"--- {len(found)} skills detected ---")
    for name, m in sorted(found.items(), key=lambda kv: (kv[1].category, kv[0])):
        print(f"[{m.category}] {name}  (via '{m.alias}')  ...{m.snippet}...")


if __name__ == "__main__":
    main()
