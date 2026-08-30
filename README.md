# Resume Job Optimizer

A Codex-compatible skill for producing truthful, job-specific, Overleaf-ready resumes with evidence-linked claims, deterministic keyword comparison, project ranking, PDF extraction checks, and separate recruiter review.

## What it solves

- Turns a candidate's verified career evidence into reusable structured data.
- Maps target-job language only to supported evidence.
- Blocks invented metrics, technologies, and unresolved evidence.
- Selects projects based on target relevance and proof strength.
- Produces a conservative single-column LaTeX source for Overleaf.
- Checks page count, extracted text, heading order, identity fields, and font embedding.
- Keeps machine checks separate from human recruiter judgment.

It does not scrape jobs, auto-apply, promise ATS ranking, or guarantee interviews.

## Quick validation

```bash
python3 scripts/verify_claims.py \
  --evidence tests/fixtures/career-evidence.yaml \
  --resume tests/fixtures/resume-valid.yaml

python3 scripts/compare_jd.py \
  --evidence tests/fixtures/career-evidence.yaml \
  --job tests/fixtures/job-description.txt

python3 scripts/render_resume.py \
  --evidence tests/fixtures/career-evidence.yaml \
  --resume tests/fixtures/resume-valid.yaml \
  --output build/resume.tex
bash scripts/compile_resume.sh build/resume.tex build tests/fixtures/career-evidence.yaml
python3 -m unittest discover -s tests -v
```

Read `SKILL.md` for the complete workflow and release gates.
