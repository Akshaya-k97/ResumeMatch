# ResumeMatch

Compare a PDF resume with a job description: see a keyword match score, matching and
missing skills, suggestions, and a downloadable report. No paid APIs, no model training.

## Run it
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
pytest
```

## How the score works
Skills are detected with a curated dictionary (`data/skills.json`) of canonical names and aliases.
Each skill in the job description is **Required** (weight 2) or **Preferred** (weight 1).
Score = weighted share of job-description skills found in the resume.
It is a keyword overlap measure, not a judgment of experience, seniority, or fit.

## Privacy
Uploaded resumes are processed in memory and never written to disk or stored.

## Known limitations
- Only skills in the dictionary are detected; extend `data/skills.json` for your field.
- No credit for related skills (e.g. MySQL does not satisfy SQL).
- "react" as an ordinary verb can match the React skill.
- Multi-column or scanned PDFs may extract poorly; check the extracted-text panel in the app.
