"""Phase 2 demo: compare a resume against a job description.

Usage:
    python run_phase2.py resume.pdf job_description.txt
    python run_phase2.py samples/sample_resume.txt samples/sample_job_description.txt
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from resumematch.extract import extract_text_from_pdf
from resumematch.matcher import WEIGHTS, analyze


def read_any(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        result = extract_text_from_pdf(path)
        for w in result.warnings:
            print(f"WARNING: {w}")
        return result.text
    return path.read_text(encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    resume_text = read_any(Path(sys.argv[1]))
    jd_text = read_any(Path(sys.argv[2]))

    result = analyze(resume_text, jd_text)
    for w in result.warnings:
        print(f"WARNING: {w}")
    if result.score is None:
        return

    print(f"Keyword match score: {result.score}%")
    print(f"  Required skills:  {result.required_matched}/{result.required_total} matched")
    print(f"  Preferred skills: {result.preferred_matched}/{result.preferred_total} matched")
    print(f"  (weights: required x{WEIGHTS['Required']}, preferred x{WEIGHTS['Preferred']})\n")

    print(result.to_dataframe()[["skill", "category", "importance", "status"]].to_string(index=False))

    if result.extra_resume_skills:
        print("\nOn your resume but not in this job description:", ", ".join(result.extra_resume_skills))


if __name__ == "__main__":
    main()
