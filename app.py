"""ResumeMatch: Streamlit app.  Run with:  streamlit run app.py"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from resumematch.extract import extract_text_from_pdf
from resumematch.matcher import WEIGHTS, analyze
from resumematch.report import build_csv, build_text_report
from resumematch.suggestions import generate_suggestions

st.set_page_config(page_title="ResumeMatch", page_icon="📄", layout="wide")

st.title("📄 ResumeMatch")
st.caption("Compare your resume with a job description and see which skills line up.")

with st.sidebar:
    st.header("How it works")
    st.markdown(
        f"""
The **keyword match score** is the weighted share of skills found in the job
description that also appear in your resume.

- Required skills count **x{WEIGHTS['Required']}**
- Preferred / nice-to-have skills count **x{WEIGHTS['Preferred']}**

It does **not** measure experience, seniority, or overall fit.
"""
    )
    include_soft = st.checkbox("Include soft skills (communication, teamwork)", value=False)
    st.header("Privacy")
    st.markdown("Your resume is processed in memory and is **not stored or saved** by this app.")

col_left, col_right = st.columns(2)
with col_left:
    uploaded = st.file_uploader("1. Upload your resume (PDF)", type=["pdf"])
with col_right:
    jd_text = st.text_area("2. Paste the job description", height=220,
                           placeholder="Paste the requirements and qualifications here...")

if st.button("3. Analyze Resume", type="primary"):
    if uploaded is None:
        st.warning("Please upload your resume as a PDF.")
    elif not jd_text.strip():
        st.warning("Please paste a job description.")
    else:
        try:
            extraction = extract_text_from_pdf(uploaded.getvalue())
        except Exception:
            st.error("Could not read that PDF. It may be corrupted or not a real PDF.")
        else:
            st.session_state["analysis"] = {
                "result": analyze(extraction.text, jd_text, include_soft_skills=include_soft),
                "resume_text": extraction.text,
                "warnings": extraction.warnings,
            }

# Results live in session_state so they survive reruns (e.g. clicking a download button).
state = st.session_state.get("analysis")
if state:
    result = state["result"]
    for w in state["warnings"] + result.warnings:
        st.warning(w)

    st.divider()
    if result.score is not None:
        m1, m2, m3 = st.columns(3)
        m1.metric("Keyword match score", f"{result.score}%")
        m2.metric("Required skills", f"{result.required_matched}/{result.required_total}")
        m3.metric("Preferred skills", f"{result.preferred_matched}/{result.preferred_total}")
        st.progress(result.score / 100)

        good, review = st.columns(2)
        with good:
            st.subheader("✅ Matching skills")
            st.write(", ".join(r.skill for r in result.matched) or "None found.")
        with review:
            st.subheader("🔍 Skills to review")
            st.write(", ".join(r.skill for r in result.missing) or "None. You covered everything detected.")

        st.subheader("💡 Suggestions")
        for tip in generate_suggestions(result):
            st.markdown(f"- {tip}")

        st.subheader("Details")
        st.dataframe(result.to_dataframe(), hide_index=True)

        d1, d2 = st.columns(2)
        d1.download_button("⬇️ Download CSV", build_csv(result), "resumematch_report.csv", "text/csv")
        d2.download_button("⬇️ Download text report", build_text_report(result), "resumematch_report.txt", "text/plain")

    with st.expander("Check the text extracted from your PDF"):
        st.caption("If this looks scrambled or incomplete, matching accuracy will suffer.")
        st.text(state["resume_text"] or "(no text extracted)")
