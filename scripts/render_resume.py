#!/usr/bin/env python3
"""Render structured resume content into the ATS LaTeX asset."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from common import load_data


def tex(value: Any) -> str:
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in str(value or ""))


def contact_block(candidate: dict[str, Any]) -> str:
    name = tex(candidate.get("name"))
    location = tex(candidate.get("location"))
    email = str(candidate.get("email", "")).strip()
    phone = str(candidate.get("phone", "")).strip()
    lines = [rf"{{\LARGE\bfseries {name}}}\\[3pt]"]
    primary = []
    if location:
        primary.append(location)
    if email:
        primary.append(rf"\href{{mailto:{tex(email)}}}{{Email: {tex(email)}}}")
    if phone:
        phone_link = re.sub(r"[^+0-9]", "", phone)
        primary.append(rf"\href{{tel:{tex(phone_link)}}}{{Phone: {tex(phone)}}}")
    if primary:
        lines.append(r" \quad | \quad ".join(primary) + r"\\[2pt]")
    secondary = []
    labels = {"linkedin": "LinkedIn", "github": "GitHub", "portfolio": "Portfolio"}
    for key, label in labels.items():
        link = str((candidate.get("links", {}) or {}).get(key, "")).strip()
        if link:
            visible = re.sub(r"^https?://(?:www\.)?", "", link).rstrip("/")
            secondary.append(rf"\href{{{tex(link)}}}{{{label}: {tex(visible)}}}")
    if secondary:
        lines.append(r" \quad | \quad ".join(secondary))
    return "\\begin{center}\n" + "\n".join(lines) + "\n\\end{center}"


def bullet_list(items: list[dict[str, Any]]) -> str:
    bullets = [rf"  \item {tex(item.get('text'))}" for item in items if str(item.get("text", "")).strip()]
    return "\\begin{itemize}\n" + "\n".join(bullets) + "\n\\end{itemize}" if bullets else ""


def experience_block(items: list[dict[str, Any]]) -> str:
    blocks = []
    for item in items:
        blocks.append(rf"\resumeEntry{{{tex(item.get('organization'))}}}{{{tex(item.get('dates'))}}}{{{tex(item.get('title'))}}}{{{tex(item.get('location'))}}}")
        blocks.append(bullet_list(item.get("bullets", []) or []))
    return "\n".join(blocks) or r"\textit{No experience entries selected.}"


def projects_block(items: list[dict[str, Any]]) -> str:
    blocks = []
    for item in items:
        tech = ", ".join(str(x) for x in item.get("technologies", []) or [])
        heading = rf"\textbf{{{tex(item.get('name'))}}}"
        if tech:
            heading += rf" \quad | \quad {tex(tech)}"
        blocks.extend([heading, bullet_list(item.get("bullets", []) or [])])
    return "\n".join(blocks) or r"\textit{No projects selected.}"


def skills_block(items: list[dict[str, Any]]) -> str:
    lines = []
    for item in items:
        values = ", ".join(str(x) for x in item.get("values", []) or [])
        if values:
            lines.append(rf"\textbf{{{tex(item.get('category'))}:}} {tex(values)}")
    return r"\\".join(lines) or r"\textit{No skills selected.}"


def education_block(items: list[dict[str, Any]]) -> str:
    lines = []
    for item in items:
        lines.append(rf"\resumeEntry{{{tex(item.get('school'))}}}{{{tex(item.get('dates'))}}}{{{tex(item.get('degree'))}}}{{{tex(item.get('location'))}}}")
    return "\n".join(lines) or r"\textit{No education entries selected.}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--resume", required=True)
    parser.add_argument("--template", default=str(Path(__file__).resolve().parents[1] / "assets" / "ats-resume.tex"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    evidence = load_data(args.evidence)
    resume = load_data(args.resume)
    candidate = evidence.get("candidate", {}) or {}
    summary = resume.get("summary", {}) or {}
    summary_text = str(summary.get("text", "")).strip()
    replacements = {
        "@@PDFTITLE@@": tex(f"{candidate.get('name', '')} Resume"),
        "@@PDFAUTHOR@@": tex(candidate.get("name", "")),
        "@@CONTACTBLOCK@@": contact_block(candidate),
        "@@SUMMARYBLOCK@@": ("\\section{Summary}\n" + tex(summary_text)) if summary_text else "",
        "@@EXPERIENCEBLOCK@@": experience_block(resume.get("experience", []) or []),
        "@@PROJECTSBLOCK@@": projects_block(resume.get("projects", []) or []),
        "@@SKILLSBLOCK@@": skills_block(resume.get("skills", []) or []),
        "@@EDUCATIONBLOCK@@": education_block(resume.get("education", []) or []),
    }
    rendered = Path(args.template).read_text(encoding="utf-8")
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)
    unresolved = re.findall(r"@@[A-Z]+@@", rendered)
    if unresolved:
        raise ValueError(f"Unresolved template tokens: {', '.join(sorted(set(unresolved)))}")
    Path(args.output).write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

