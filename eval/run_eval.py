"""Evaluate skill extraction and score ranking on the small hand-labeled sets in this folder.

Usage:  python eval/run_eval.py     (writes eval/RESULTS.md)
"""
import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from resumematch.matcher import analyze
from resumematch.normalize import normalize_text
from resumematch.skills import find_skills

BLEND_WEIGHT = 0.3  # fixed in advance, NOT tuned on this set


def eval_extraction():
    cases = json.loads((HERE / "extraction_cases.json").read_text(encoding="utf-8"))
    tp = fp = fn = 0
    errors = []
    for c in cases:
        got = set(find_skills(normalize_text(c["text"])))
        exp = set(c["expected"])
        tp += len(got & exp); fp += len(got - exp); fn += len(exp - got)
        if got != exp:
            errors.append((c["text"], sorted(got - exp), sorted(exp - got), c.get("note", "")))
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return len(cases), p, r, f1, errors


def method_scores(resume, jd):
    base = analyze(resume, jd, use_related=False)
    rel = analyze(resume, jd, use_related=True)
    kw, kr = base.score or 0, rel.score or 0
    sim = rel.text_similarity or 0
    return {
        "keyword only": kw,
        "keyword + related": kr,
        "text similarity only": sim,
        f"blend ({int((1 - BLEND_WEIGHT) * 100)}% keyword+related / {int(BLEND_WEIGHT * 100)}% similarity)":
            round((1 - BLEND_WEIGHT) * kr + BLEND_WEIGHT * sim),
    }


def eval_ranking():
    data = json.loads((HERE / "ranking_cases.json").read_text(encoding="utf-8"))
    scores = {(rid, jid): method_scores(r["text"], jd)
              for rid, r in data["resumes"].items() for jid, jd in data["jds"].items()}
    methods = list(next(iter(scores.values())))
    results = {m: {"correct": 0, "ties": 0, "total": 0} for m in methods}
    wrong = []  # misordered pairs for the main method
    for jid in data["jds"]:
        for a, b in combinations(data["resumes"], 2):
            la, lb = data["resumes"][a]["labels"][jid], data["resumes"][b]["labels"][jid]
            if la == lb:
                continue
            hi, lo = (a, b) if la > lb else (b, a)
            for m in methods:
                results[m]["total"] += 1
                sh, sl = scores[(hi, jid)][m], scores[(lo, jid)][m]
                if sh > sl:
                    results[m]["correct"] += 1
                elif sh == sl:
                    results[m]["ties"] += 1
                if m == "keyword + related" and sh <= sl:
                    wrong.append(f"{jid}: {hi} (label {max(la, lb)}, {sh}%) vs {lo} (label {min(la, lb)}, {sl}%)")
    return data, scores, results, wrong


def main():
    n, p, r, f1, errors = eval_extraction()
    data, scores, results, wrong = eval_ranking()
    out = ["# Evaluation results", "",
           "Small hand-written sets (see the JSON files). These numbers demonstrate the method on",
           "a limited, partly self-authored test set; they are not a claim of general accuracy.", "",
           f"## 1. Skill extraction ({n} labeled snippets, dictionary skills only)", "",
           f"- Precision: **{p:.2f}**", f"- Recall: **{r:.2f}**", f"- F1: **{f1:.2f}**", ""]
    if errors:
        out += ["Mismatches:", ""]
        for text, extra, missed, note in errors:
            out.append(f"- \"{text}\"  extra: {extra or '-'}  missed: {missed or '-'}" + (f"  ({note})" if note else ""))
        out.append("")

    out += ["## 2. Score ranking", "",
            "For every job description, each pair of resumes with different human fit labels should be",
            "ordered correctly (higher label gets a strictly higher score). Ties count as failures.", "",
            "| Method | Correct pairs | Ties | Accuracy |", "|---|---|---|---|"]
    for m, v in results.items():
        out.append(f"| {m} | {v['correct']}/{v['total']} | {v['ties']} | {v['correct'] / v['total']:.0%} |")

    if wrong:
        out += ["", "Misordered pairs (keyword + related):", ""] + [f"- {w}" for w in wrong]

    out += ["", "### Scores by resume and job (keyword + related)", "",
            "| Resume | " + " | ".join(data["jds"]) + " |", "|---|" + "---|" * len(data["jds"])]
    for rid in data["resumes"]:
        cells = [f"{scores[(rid, j)]['keyword + related']}% (label {data['resumes'][rid]['labels'][j]})" for j in data["jds"]]
        out.append(f"| {rid} | " + " | ".join(cells) + " |")

    report = "\n".join(out) + "\n"
    (HERE / "RESULTS.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
