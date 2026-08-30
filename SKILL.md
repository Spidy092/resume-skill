---
name: resume-job-optimizer
description: Build or tailor truthful ATS-safe resumes from verified career evidence and a target job, including project selection, keyword mapping, Overleaf-ready LaTeX, PDF extraction checks, and recruiter review. Use for resume creation or job-specific resume optimization; do not use for job scraping, automatic applications, or interview coaching.
---

# Resume Job Optimizer

Produce a resume whose claims are traceable, whose job keywords are supported by evidence, whose PDF is machine-readable, and whose first page communicates fit quickly to a human reviewer.

## Non-negotiable invariants

1. Treat `career-evidence.yaml` as the factual source of truth. Never invent scope, metrics, dates, titles, technologies, ownership, or outcomes.
2. A missing job requirement is a gap, not permission to add it. Distinguish `supported`, `adjacent`, `unsupported`, and `unknown` evidence.
3. Do not optimize toward a proprietary ATS score. Optimize observable parsing, supported requirement coverage, and recruiter comprehension.
4. Keep the canonical resume content structured and render LaTeX from it. Do not make an untracked edit only in the PDF.
5. Do not submit applications, contact people, or modify external profiles without a separate explicit request.

## Inputs

Require career evidence using `templates/career-evidence.yaml` or source material sufficient to build it, a target role or pasted job description, and locale/page-limit choices when they materially affect the result.

If evidence is incomplete, read `references/evidence-interview.md` and ask only questions that can change claim truth, project selection, or positioning. Do not block on cosmetic preferences.

## Workflow

### 1. Establish evidence

Normalize source material into stable evidence IDs. Preserve uncertainty and sensitivity markers. Validate it:

```bash
python3 scripts/verify_claims.py --evidence career-evidence.yaml --validate-evidence
```

Stop resume generation if the evidence schema is invalid.

### 2. Analyze the target job

Read `references/keyword-mapping.md` and `references/project-scoring.md`. Generate a deterministic baseline:

```bash
python3 scripts/compare_jd.py --evidence career-evidence.yaml --job job-description.txt \
  --json-out job-analysis.json --markdown-out job-analysis.md
```

Interpret matches rather than copying the output blindly. Separate required from preferred language, supported from unsupported keywords, and direct from adjacent evidence.

### 3. Choose positioning and content

Select evidence that proves the target role. Prefer work experience over projects when both prove the same capability. Prefer two strong, relevant projects over a long project inventory.

Write each bullet as a compact claim with linked `evidence_ids`. Quantify only when the linked evidence contains the same quantity or an explicitly documented derivation. Store the draft using the structured contract in `references/evidence-interview.md`.

Before rendering, run:

```bash
python3 scripts/verify_claims.py --evidence career-evidence.yaml \
  --resume resume-content.yaml --report claim-report.json
```

Any error blocks release. Warnings require review.

### 4. Render the Overleaf source

Use `assets/ats-resume.tex` as the rendering base. Preserve its single-column reading order, text labels, Unicode mapping, standard headings, and PDF metadata. Render deterministically so escaping and repeated sections remain consistent:

```bash
python3 scripts/render_resume.py --evidence career-evidence.yaml \
  --resume resume-content.yaml --output resume.tex
```

Compile locally when TeX is available:

```bash
bash scripts/compile_resume.sh resume.tex build career-evidence.yaml
```

The `.tex` source must remain directly uploadable to Overleaf. Do not require shell escape or hosted fonts.

### 5. Audit the PDF

Read `references/ats-rules.md`. `compile_resume.sh` invokes `audit_pdf.py`; run it separately when evaluating an existing PDF:

```bash
python3 scripts/audit_pdf.py --pdf build/resume.pdf \
  --evidence career-evidence.yaml \
  --expected-headings "Experience,Projects,Skills,Education" \
  --max-pages 1 --json-out build/pdf-audit.json
```

Parsing errors, missing identity fields, broken text order, overflow, or unembedded fonts block release. A clean extraction does not prove that a particular employer ATS will rank the resume.

### 6. Review like a human

Read `references/recruiter-rubric.md`. Perform three distinct passes: 10-second scan, hiring-manager evidence review, and skeptical claim review. Complete `templates/resume-review.md`. Do not collapse these into one synthetic score.

### 7. Deliver

Return editable `.tex`, a compiled PDF when local TeX is available, structured resume content, job analysis and gap report, claim/PDF audit reports, and the recruiter review. Separate blocking issues from optional improvements.

State limitations plainly. Never promise interviews, ATS acceptance, or a callback rate.

## Optional integrations

- Use a connected resume parser or diagnosis tool as a second opinion after deterministic checks. Never let it overwrite evidence or silently patch content.
- Use GitHub read-only inspection to collect project evidence when the user provides or authorizes repositories. Repository contents prove implementation, not business impact or personal ownership by themselves.
- Use Overleaf for collaborative editing; local compilation remains the repeatable release gate.
