#!/usr/bin/env python3
"""Shared, dependency-light helpers for resume-job-optimizer."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml


def load_data(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        if source.suffix.lower() == ".json":
            data = json.load(handle)
        else:
            data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{source} must contain a mapping at the top level")
    return data


def normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9+#.]+", " ", text.casefold()).strip()


def contains_term(text: str, term: str) -> bool:
    haystack = f" {normalized(text)} "
    needle = normalized(term)
    if not needle:
        return False
    return re.search(rf"(?<![a-z0-9+#.]){re.escape(needle)}(?![a-z0-9+#.])", haystack) is not None


def dump_json(data: Any, path: str | Path | None) -> None:
    rendered = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
    if path:
        Path(path).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


def evidence_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in data.get("evidence", []) or []:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            result[item["id"]] = item
    return result


def skill_catalog(data: dict[str, Any]) -> list[dict[str, Any]]:
    catalog: list[dict[str, Any]] = []
    aliases_map = data.get("aliases", {}) or {}
    for raw in data.get("skills", []) or []:
        if isinstance(raw, str):
            name, evidence_ids, aliases = raw, [], aliases_map.get(raw, [])
        elif isinstance(raw, dict) and raw.get("name"):
            name = str(raw["name"])
            evidence_ids = list(raw.get("evidence_ids", []) or [])
            aliases = list(raw.get("aliases", []) or aliases_map.get(name, []) or [])
        else:
            continue
        catalog.append({"name": name, "aliases": aliases, "evidence_ids": evidence_ids})
    return catalog

