# Contributing

Contributions should improve the specific workflow this project promises: evidence-grounded resume writing, supported job matching, project selection, Overleaf output, deterministic verification, or recruiter review.

## Before opening a pull request

1. Open an issue for a large behavior change so its scope can be agreed first.
2. Do not include real resumes, contact details, employer-confidential data, or fabricated examples.
3. Keep the skill instructions concise. Put detailed rules in `references/` and deterministic work in `scripts/`.
4. Add or update fixtures and tests for behavior changes.
5. Run:

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
npx skills add . --list
```

PDF-related changes should also be tested with LaTeX and Poppler installed.

## Pull request scope

Prefer one problem per pull request. Explain the user problem, the evidence for the change, the verification performed, and any limitations. Changes must preserve the rule that unsupported experience remains a gap rather than becoming a resume claim.
