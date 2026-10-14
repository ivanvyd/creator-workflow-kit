"""Constrained run-directory and JSON helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path

import tomllib

SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def runs_root() -> Path:
    path = repo_root() / "config.toml"
    configured = "runs"
    if path.exists():
        configured = tomllib.loads(path.read_text(encoding="utf-8")).get("paths", {}).get("runs_dir", "runs")
    if not isinstance(configured, str) or not re.fullmatch(r"[a-zA-Z0-9_-]+", configured):
        raise ValueError("paths.runs_dir must be one simple relative directory name")
    return repo_root() / configured


def valid_slug(value: str) -> str:
    if len(value) > 48 or not SLUG_RE.fullmatch(value):
        raise ValueError("slug must be 1-48 lowercase letters, digits, and single hyphens")
    return value


def confined(root: Path, candidate: Path) -> Path:
    root = root.resolve()
    resolved = candidate.resolve()
    if resolved == root or root not in resolved.parents:
        raise ValueError("path escapes the configured runs directory")
    return resolved


def job_path(slug: str, *, create: bool = False) -> Path:
    valid_slug(slug)
    path = confined(runs_root(), runs_root() / slug)
    if create:
        path.mkdir(parents=True, exist_ok=False)
    return path


def write_json_new(path: Path, value: object) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))
