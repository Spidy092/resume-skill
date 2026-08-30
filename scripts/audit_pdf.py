#!/usr/bin/env python3
"""Deterministically audit a resume PDF's extractability and basic structure."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from common import dump_json, load_data


def run(command: list[str]) -> str:
    executable = shutil.which(command[0])
    if not executable:
        raise RuntimeError(f"Required executable not found: {command[0]}")
    completed = subprocess.run([executable, *command[1:]], check=False, capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError(f"{' '.join(command)} failed: {completed.stderr.strip()}")
    return completed.stdout


def page_count(pdf: Path) -> int:
    info = run(["pdfinfo", str(pdf)])
    match = re.search(r"^Pages:\s+(\d+)", info, re.M)
    if not match:
        raise RuntimeError("pdfinfo did not report a page count")
    return int(match.group(1))


def unembedded_fonts(pdf: Path) -> list[str]:
    output = run(["pdffonts", str(pdf)])
    bad = []
    for line in output.splitlines()[2:]:
        if not line.strip():
            continue
        columns = line.split()
        yes_no = [i for i, value in enumerate(columns) if value in {"yes", "no"}]
        if yes_no and columns[yes_no[0]] == "no":
            bad.append(columns[0])
    return bad


def expected_identity(evidence_path: str | None) -> list[tuple[str, str]]:
    if not evidence_path:
        return []
    candidate = load_data(evidence_path).get("candidate", {}) or {}
    fields = [("name", candidate.get("name", "")), ("email", candidate.get("email", "")), ("phone", candidate.get("phone", ""))]
    return [(name, str(value).strip()) for name, value in fields if str(value).strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--evidence")
    parser.add_argument("--expected-headings", default="Experience,Projects,Skills,Education")
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--min-characters", type=int, default=400)
    parser.add_argument("--json-out")
    parser.add_argument("--text-out")
    args = parser.parse_args()

    pdf = Path(args.pdf)
    issues: list[dict[str, str]] = []
    if not pdf.is_file():
        issues.append({"severity": "error", "check": "file", "message": f"PDF not found: {pdf}"})
        dump_json({"status": "fail", "issues": issues}, args.json_out)
        return 1

    try:
        with tempfile.TemporaryDirectory(prefix="resume-audit-") as temp:
            text_path = Path(temp) / "resume.txt"
            run(["pdftotext", "-enc", "UTF-8", str(pdf), str(text_path)])
            text = text_path.read_text(encoding="utf-8", errors="replace")
        if args.text_out:
            Path(args.text_out).write_text(text, encoding="utf-8")
        pages = page_count(pdf)
        fonts = unembedded_fonts(pdf)
    except RuntimeError as error:
        issues.append({"severity": "error", "check": "tooling", "message": str(error)})
        dump_json({"status": "fail", "issues": issues}, args.json_out)
        return 1

    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) < args.min_characters:
        issues.append({"severity": "error", "check": "extraction", "message": f"Only {len(compact)} extracted characters; expected at least {args.min_characters}"})
    if "�" in text or "[NULL]" in text:
        issues.append({"severity": "error", "check": "encoding", "message": "Replacement or NULL glyph found in extracted text"})
    if pages > args.max_pages:
        issues.append({"severity": "error", "check": "page_count", "message": f"PDF has {pages} pages; maximum is {args.max_pages}"})
    for field, value in expected_identity(args.evidence):
        if value.casefold() not in text.casefold():
            issues.append({"severity": "error", "check": "identity", "message": f"Candidate {field} is missing from extracted text"})
    headings = [x.strip() for x in args.expected_headings.split(",") if x.strip()]
    positions = []
    for heading in headings:
        match = re.search(rf"(?im)^\s*{re.escape(heading)}\s*$", text)
        if not match:
            issues.append({"severity": "error", "check": "headings", "message": f"Expected heading missing: {heading}"})
        else:
            positions.append((heading, match.start()))
    if positions != sorted(positions, key=lambda item: item[1]):
        issues.append({"severity": "error", "check": "reading_order", "message": "Expected headings are not in the requested order"})
    if fonts:
        issues.append({"severity": "error", "check": "fonts", "message": f"Unembedded fonts: {', '.join(fonts)}"})

    report: dict[str, Any] = {
        "status": "fail" if any(x["severity"] == "error" for x in issues) else "pass",
        "pdf": str(pdf.resolve()),
        "pages": pages,
        "extracted_characters": len(compact),
        "unembedded_fonts": fonts,
        "issues": issues,
        "limitations": ["A passing result does not reproduce or predict every employer ATS."],
    }
    dump_json(report, args.json_out)
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())

