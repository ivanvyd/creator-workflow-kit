"""Scan tracked source candidates without opening ignored credential locations."""

from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".venv", "runs", "credentials", "__pycache__", ".pytest_cache", "node_modules", "renders", ".hyperframes"}
PATTERNS = {
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "openai-key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "google-key": re.compile(r"\bAIza[\w-]{20,}\b"),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "inline-secret-assignment": re.compile(r"(?i)\b(?:api[_-]?key|password|secret|token)\s*=\s*['\"][^'\"]{8,}"),
}


def scan(root: Path) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for directory, directories, filenames in os.walk(root):
        directories[:] = [name for name in directories if name not in SKIP_PARTS]
        for filename in filenames:
            path = Path(directory) / filename
            if path.name.startswith(".env") or path.suffix in {".mp4", ".png", ".mp3"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for label, pattern in PATTERNS.items():
                if pattern.search(text):
                    findings.append((str(path.relative_to(root)), label))
    return findings


def main() -> int:
    findings = scan(ROOT)
    if findings:
        for path, label in findings:
            print(f"suspected {label}: {path} (content redacted)")
        return 1
    print("OK: checked repository source files; no suspected credential tokens found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
