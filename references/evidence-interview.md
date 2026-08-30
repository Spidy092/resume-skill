# Evidence intake and content contract

Ask only questions whose answers can change the resume, in this order:

1. Target role, level, geography, and job family.
2. Employment dates, exact titles, and employer names.
3. Personal contribution versus team contribution.
4. Production scope: users, traffic, environments, availability, data size, or release frequency.
5. Outcomes and how each number was measured.
6. Technologies actually used by the candidate.
7. Incidents, migrations, security work, performance work, and difficult decisions.
8. Projects with source, demo, users, or other verifiable artifacts.
9. Education, certifications, work authorization, and languages when job-relevant.

For an unknown metric, record `null`; do not pressure the candidate into estimating. Record a derivation only when its inputs and method are available.

## Evidence quality

- `verified`: supported by a source or explicit candidate confirmation.
- `candidate_confirmed`: asserted by the candidate but not independently checked.
- `derived`: calculated from documented inputs; store the derivation.
- `unknown`: incomplete or ambiguous; never publish as fact.
- `disputed`: sources conflict; resolve before use.

## Structured resume content

Create `resume-content.yaml` before writing LaTeX:

```yaml
target:
  title: Platform Engineer
  company: Example Corp
summary:
  text: Platform engineer focused on reliable delivery systems.
  evidence_ids: [role-acme, project-release]
experience:
  - organization: Acme
    title: Software Engineer
    dates: 2023-01 to present
    bullets:
      - text: Built a GitHub Actions release pipeline for a Node.js service.
        evidence_ids: [achievement-release-pipeline]
        target_keywords: [GitHub Actions, Node.js]
projects: []
skills:
  - category: Cloud and delivery
    values: [AWS, Docker, GitHub Actions]
education: []
```

Every factual summary sentence and bullet needs at least one evidence ID. Contact data and section labels do not.

## Claim boundaries

- “Built” means the candidate implemented a material part.
- “Led” means the candidate directed people or decisions, not merely attended.
- “Owned” means sustained accountability, not one contribution.
- “Architected” requires a meaningful system-level design decision.
- Team results must be worded as team results unless individual causality is evidenced.
- A repository proves code exists. It cannot alone prove production usage, employer adoption, revenue, or the candidate's exact contribution.

