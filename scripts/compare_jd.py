#!/usr/bin/env python3
"""Compare a job description with declared evidence and rank projects."""

from __future__ import annotations

import argparse
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from common import contains_term, dump_json, evidence_index, load_data, normalized, skill_catalog

REQUIRED = re.compile(r"\b(must|required|requirements?|minimum|need(?:ed)?|you have)\b", re.I)
PREFERRED = re.compile(r"\b(preferred|nice to have|bonus|ideally|plus)\b", re.I)
STOPWORDS = {
    "about", "after", "also", "and", "are", "been", "but", "can", "company",
    "experience", "for", "from", "has", "have", "into", "is", "job", "must", "our",
    "preferred", "required", "role", "that", "the", "their", "this", "those", "to",
    "using", "we", "will", "with", "work", "years", "you", "your",
}


def sentences(text: str) -> list[str]:
    return [s.strip(" \t\n-•") for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.strip()) > 8]


def requirement_rows(text: str) -> list[dict[str, str]]:
    rows = []
    for sentence in sentences(text):
        priority = "required" if REQUIRED.search(sentence) else "preferred" if PREFERRED.search(sentence) else "other"
        if priority != "other":
            rows.append({"priority": priority, "text": sentence})
    return rows


def candidate_terms(text: str, limit: int = 25) -> list[dict[str, Any]]:
    words = [w.strip(".-") for w in re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{1,}", text)]
    words = [w for w in words if w and w.casefold() not in STOPWORDS]
    counts = Counter(normalized(w) for w in words)
    display: dict[str, str] = {}
    for word in words:
        display.setdefault(normalized(word), word)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{"term": display[key], "count": count} for key, count in ranked[:limit] if count >= 2]


def match_skills(data: dict[str, Any], job: str) -> list[dict[str, Any]]:
    matches = []
    for skill in skill_catalog(data):
        matched_as = None
        classification = "not_requested"
        if contains_term(job, skill["name"]):
            matched_as, classification = skill["name"], "supported_direct"
        else:
            for alias in skill["aliases"]:
                if contains_term(job, str(alias)):
                    matched_as, classification = str(alias), "supported_alias"
                    break
        matches.append({
            "canonical": skill["name"],
            "matched_as": matched_as,
            "classification": classification,
            "evidence_ids": skill["evidence_ids"],
        })
    return matches


def project_scores(data: dict[str, Any], requested: set[str]) -> list[dict[str, Any]]:
    rows = []
    for project in data.get("projects", []) or []:
        if not isinstance(project, dict):
            continue
        pskills = {normalized(str(s)) for s in project.get("skills", []) or []}
        relevance = len(pskills & requested) / max(1, len(requested))
        component = lambda key: max(0.0, min(5.0, float(project.get("ratings", {}).get(key, 0)))) / 5.0
        uniqueness = component("uniqueness")
        score = 100 * (
            0.35 * relevance
            + 0.20 * component("impact")
            + 0.15 * component("complexity")
            + 0.15 * component("production")
            + 0.10 * component("verifiability")
            + 0.05 * uniqueness
        )
        rows.append({
            "id": project.get("id"),
            "name": project.get("name", project.get("id", "Unnamed project")),
            "score": round(score, 1),
            "matched_skills": sorted(pskills & requested),
            "evidence_ids": project.get("evidence_ids", []),
        })
    return sorted(rows, key=lambda row: (-row["score"], str(row["name"])))


def markdown_report(result: dict[str, Any]) -> str:
    lines = ["# Deterministic job comparison", "", "> Baseline only. Review job context and evidence before changing a resume.", ""]
    lines += ["## Evidence-backed job terms", "", "| Canonical term | Match | Classification | Evidence |", "|---|---|---|---|"]
    for row in result["skill_matches"]:
        if row["classification"] != "not_requested":
            lines.append(f"| {row['canonical']} | {row['matched_as']} | {row['classification']} | {', '.join(row['evidence_ids'])} |")
    lines += ["", "## Explicit requirement sentences", ""]
    for row in result["requirements"]:
        lines.append(f"- **{row['priority']}**: {row['text']}")
    lines += ["", "## Project ranking", "", "| Project | Score | Matched target skills |", "|---|---:|---|"]
    for row in result["project_scores"]:
        lines.append(f"| {row['name']} | {row['score']:.1f} | {', '.join(row['matched_skills'])} |")
    lines += ["", "## Repeated job-description terms requiring review", ""]
    lines.append(", ".join(f"{x['term']} ({x['count']})" for x in result["candidate_terms"]) or "None")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--json-out")
    parser.add_argument("--markdown-out")
    args = parser.parse_args()
    data = load_data(args.evidence)
    job = Path(args.job).read_text(encoding="utf-8")
    matches = match_skills(data, job)
    requested = {normalized(row["canonical"]) for row in matches if row["classification"].startswith("supported")}
    result = {
        "requirements": requirement_rows(job),
        "skill_matches": matches,
        "candidate_terms": candidate_terms(job),
        "project_scores": project_scores(data, requested),
        "limitations": [
            "This matcher uses declared skills and aliases; it does not infer unsupported experience.",
            "Repeated terms are review candidates, not automatic resume keywords.",
        ],
    }
    dump_json(result, args.json_out)
    if args.markdown_out:
        Path(args.markdown_out).write_text(markdown_report(result), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
