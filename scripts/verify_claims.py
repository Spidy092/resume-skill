#!/usr/bin/env python3
"""Validate evidence and ensure resume claims link to compatible evidence."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Iterator

from common import contains_term, dump_json, evidence_index, load_data, normalized, skill_catalog

QUALITIES = {"verified", "candidate_confirmed", "derived", "unknown", "disputed"}
STRONG_VERBS = re.compile(r"\b(architected|owned|led|increased|reduced|saved|generated)\b", re.I)
NUMBER = re.compile(r"(?<![A-Za-z])(?:\d+(?:\.\d+)?%?|\$\d+(?:\.\d+)?[KMB]?)", re.I)


def evidence_text(item: dict[str, Any]) -> str:
    parts = [str(item.get("statement", "")), str(item.get("derivation", ""))]
    parts.extend(str(x) for x in item.get("technologies", []) or [])
    metrics = item.get("metrics", {}) or {}
    if isinstance(metrics, dict):
        parts.extend(f"{k} {v}" for k, v in metrics.items())
    return " ".join(parts)


def claims(node: Any, path: str = "") -> Iterator[tuple[str, dict[str, Any]]]:
    if isinstance(node, dict):
        if isinstance(node.get("text"), str) and "evidence_ids" in node:
            yield path or "root", node
        for key, value in node.items():
            child = f"{path}.{key}" if path else str(key)
            yield from claims(value, child)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from claims(value, f"{path}[{index}]")


def validate_evidence(data: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if data.get("schema_version") != 1:
        issues.append({"severity": "error", "path": "schema_version", "message": "Expected schema_version: 1"})
    candidate = data.get("candidate")
    if not isinstance(candidate, dict) or not str(candidate.get("name", "")).strip():
        issues.append({"severity": "error", "path": "candidate.name", "message": "Candidate name is required"})
    seen: set[str] = set()
    for index, item in enumerate(data.get("evidence", []) or []):
        path = f"evidence[{index}]"
        if not isinstance(item, dict):
            issues.append({"severity": "error", "path": path, "message": "Evidence item must be a mapping"})
            continue
        evidence_id = item.get("id")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            issues.append({"severity": "error", "path": f"{path}.id", "message": "Stable evidence ID is required"})
        elif evidence_id in seen:
            issues.append({"severity": "error", "path": f"{path}.id", "message": f"Duplicate evidence ID: {evidence_id}"})
        else:
            seen.add(evidence_id)
        if item.get("quality") not in QUALITIES:
            issues.append({"severity": "error", "path": f"{path}.quality", "message": f"Quality must be one of {sorted(QUALITIES)}"})
        if not str(item.get("statement", "")).strip():
            issues.append({"severity": "error", "path": f"{path}.statement", "message": "Evidence statement is required"})
    return issues


def verify_resume(data: dict[str, Any], resume: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    index = evidence_index(data)
    catalog = skill_catalog(data)
    for path, claim in claims(resume):
        text = claim["text"].strip()
        ids = claim.get("evidence_ids") or []
        if not ids:
            issues.append({"severity": "error", "path": path, "message": "Factual claim has no evidence IDs"})
            continue
        unknown = [evidence_id for evidence_id in ids if evidence_id not in index]
        if unknown:
            issues.append({"severity": "error", "path": path, "message": f"Unknown evidence IDs: {', '.join(unknown)}"})
            continue
        linked = [index[evidence_id] for evidence_id in ids]
        linked_text = " ".join(evidence_text(item) for item in linked)
        low_quality = [item["id"] for item in linked if item.get("quality") in {"unknown", "disputed"}]
        if low_quality:
            issues.append({"severity": "error", "path": path, "message": f"Claim relies on unresolved evidence: {', '.join(low_quality)}"})
        for number in NUMBER.findall(text):
            plain = number.replace(",", "")
            if plain.isdigit() and 1900 <= int(plain) <= 2100:
                continue
            if normalized(number) not in normalized(linked_text):
                issues.append({"severity": "error", "path": path, "message": f"Quantity '{number}' is absent from linked evidence"})
        for skill in catalog:
            terms = [skill["name"], *skill["aliases"]]
            used = next((term for term in terms if contains_term(text, str(term))), None)
            if used and not any(contains_term(linked_text, str(term)) for term in terms):
                issues.append({"severity": "error", "path": path, "message": f"Technology '{used}' is absent from linked evidence"})
        for keyword in claim.get("target_keywords", []) or []:
            if contains_term(text, str(keyword)) and not contains_term(linked_text, str(keyword)):
                issues.append({"severity": "error", "path": path, "message": f"Target keyword '{keyword}' is absent from linked evidence"})
        if STRONG_VERBS.search(text) and not any(item.get("quality") == "verified" for item in linked):
            issues.append({"severity": "warning", "path": path, "message": "Strong ownership/outcome verb has no independently verified evidence"})
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--resume")
    parser.add_argument("--validate-evidence", action="store_true")
    parser.add_argument("--report")
    args = parser.parse_args()
    data = load_data(args.evidence)
    issues = validate_evidence(data)
    if args.resume:
        issues.extend(verify_resume(data, load_data(args.resume)))
    elif not args.validate_evidence:
        parser.error("provide --resume or --validate-evidence")
    report = {
        "status": "fail" if any(x["severity"] == "error" for x in issues) else "pass_with_warnings" if issues else "pass",
        "errors": sum(x["severity"] == "error" for x in issues),
        "warnings": sum(x["severity"] == "warning" for x in issues),
        "issues": issues,
    }
    dump_json(report, args.report)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
