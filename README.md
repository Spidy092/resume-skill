# Resume Job Optimizer

An open-source Agent Skill for producing truthful, job-specific, Overleaf-ready resumes. It links every resume claim to career evidence, compares supported job keywords, ranks projects, renders conservative LaTeX, audits PDF extraction, and keeps automated checks separate from human recruiter review.

It does **not** scrape jobs, auto-apply, invent credentials, promise ATS ranking, or guarantee interviews.

## Install

The skill is distributed directly from this GitHub repository through the open-source [Skills CLI](https://github.com/vercel-labs/skills). You do not need to install this repository as an npm package.

```bash
npx skills add Spidy092/resume-skill
```

Install globally for Codex without interactive prompts:

```bash
npx skills add Spidy092/resume-skill \
  --skill resume-job-optimizer --agent codex --global --yes
```

Inspect the skill without installing it:

```bash
npx skills use Spidy092/resume-skill@resume-job-optimizer
```

The CLI also supports Claude Code, Cursor, OpenCode, and other compatible agents. Select the appropriate agent during interactive installation or pass its identifier with `--agent`.

## Requirements

- An Agent Skills-compatible coding agent
- Python 3.10+
- Python packages from `requirements.txt`
- Optional for PDF output: `latexmk`, a LaTeX distribution, `pdftotext`, and `pdffonts`
- Overleaf needs only the generated `.tex`; the template does not require shell escape or hosted fonts

Install the Python dependency for local script use:

```bash
python3 -m pip install -r requirements.txt
```

## Use

Ask your agent to invoke the installed skill and provide a target job description plus truthful source material such as an existing resume, portfolio, or career notes.

Example prompt:

```text
Use $resume-job-optimizer. Build my career-evidence file from the material I provide,
analyze this job description, select the strongest relevant projects, and produce an
Overleaf-ready resume. Do not invent missing facts; show unsupported requirements as gaps.
```

The skill's workflow is:

1. Normalize and validate career evidence.
2. Compare the target job with supported evidence.
3. Select relevant work and projects.
4. Verify every drafted claim.
5. Render an Overleaf-compatible LaTeX resume.
6. Compile and audit the PDF when local tools are available.
7. Review it separately for recruiter readability.

See [`SKILL.md`](SKILL.md) for the complete workflow and release gates.

## Local validation

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

bash scripts/compile_resume.sh \
  build/resume.tex build tests/fixtures/career-evidence.yaml

python3 -m unittest discover -s tests -v
npx skills add . --list
```

## Privacy and trust

Resume data contains personal information. Review files before committing them, keep real candidate evidence out of public issues and pull requests, and inspect scripts before installing any third-party skill. This repository performs local file processing and does not submit applications or contact employers.

## Contributing

Bug reports and focused pull requests are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before contributing and report security issues using [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
