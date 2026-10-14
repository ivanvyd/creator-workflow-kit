"""List or explicitly clone reviewed public skill references into a chosen directory."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

SOURCES = {
    "elevenlabs-skills": ("https://github.com/elevenlabs/skills.git", "0e371300354872fbb8ee375f04cf518e9a335ca5", "MIT"),
    "hyperframes": ("https://github.com/heygen-com/hyperframes.git", "38cfcdd56cdc1a8125a8e68a3604357a23ce819f", "Apache-2.0"),
    "hand-drawn-diagrams": ("https://github.com/muthuishere/hand-drawn-diagrams.git", "c8ffd6c3febbc0e745ab6691ea81c8703a9829c8", "MIT with upstream notices"),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--install", choices=sorted(SOURCES))
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    if args.list:
        for name, (_, commit, license_name) in SOURCES.items():
            print(f"{name}: {commit} ({license_name})")
        return
    if not args.install or not args.destination:
        parser.error("choose --list or --install NAME --destination DIRECTORY")
    url, commit, _ = SOURCES[args.install]
    destination = args.destination / args.install
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    subprocess.run(["git", "clone", "--no-checkout", url, str(destination)], check=True)
    subprocess.run(["git", "-C", str(destination), "checkout", "--detach", commit], check=True)


if __name__ == "__main__":
    main()
