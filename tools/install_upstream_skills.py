"""List or explicitly clone reviewed public skill references into a chosen directory."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "elevenlabs-skills": ("https://github.com/elevenlabs/skills.git", "0e371300354872fbb8ee375f04cf518e9a335ca5", "MIT"),
    "hyperframes": ("https://github.com/heygen-com/hyperframes.git", "38cfcdd56cdc1a8125a8e68a3604357a23ce819f", "Apache-2.0"),
    "hand-drawn-diagrams": ("https://github.com/muthuishere/hand-drawn-diagrams.git", "c8ffd6c3febbc0e745ab6691ea81c8703a9829c8", "MIT with upstream notices"),
}
HYPERFRAMES_SKILLS = ("hyperframes-core", "hyperframes-animation", "hyperframes-creative", "hyperframes-cli")
HYPERFRAMES_URL, HYPERFRAMES_COMMIT, _ = SOURCES["hyperframes"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--install", choices=sorted(SOURCES))
    parser.add_argument("--install-hyperframes-skills", action="store_true")
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    if args.list:
        for name, (_, commit, license_name) in SOURCES.items():
            print(f"{name}: {commit} ({license_name})")
        return
    if not args.destination or (not args.install and not args.install_hyperframes_skills) or (args.install and args.install_hyperframes_skills):
        parser.error("choose --list, --install NAME --destination DIRECTORY, or --install-hyperframes-skills --destination DIRECTORY")
    if args.install_hyperframes_skills:
        repository = ROOT.resolve()
        destination = args.destination.resolve()
        if destination != repository and repository not in destination.parents:
            raise SystemExit("HyperFrames skills must be installed inside the current repository")
        targets = [destination / name for name in HYPERFRAMES_SKILLS]
        existing = [str(path) for path in targets if path.exists() or path.is_symlink()]
        if existing:
            raise SystemExit("refusing to overwrite existing skill directories: " + ", ".join(existing))
        with tempfile.TemporaryDirectory(prefix="creator-kit-hyperframes-") as temporary:
            checkout = Path(temporary) / "hyperframes"
            subprocess.run(["git", "clone", "--no-checkout", HYPERFRAMES_URL, str(checkout)], check=True)
            subprocess.run(["git", "-C", str(checkout), "checkout", "--detach", HYPERFRAMES_COMMIT], check=True)
            sources = [checkout / "skills" / name for name in HYPERFRAMES_SKILLS]
            missing = [str(path) for path in sources if not path.is_dir()]
            license_path = checkout / "LICENSE"
            if missing or not license_path.is_file():
                details = ", ".join(missing or [str(license_path)])
                raise SystemExit(f"pinned HyperFrames source is missing required files: {details}")
            notice_path = checkout / "NOTICE"
            staged = Path(temporary) / "selected-skills"
            for name, source in zip(HYPERFRAMES_SKILLS, sources, strict=True):
                skill = staged / name
                shutil.copytree(source, skill)
                shutil.copy2(license_path, skill / "LICENSE")
                if notice_path.is_file():
                    shutil.copy2(notice_path, skill / "NOTICE")
                (skill / "UPSTREAM_PROVENANCE.md").write_text(
                    f"Source: {HYPERFRAMES_URL}\nCommit: {HYPERFRAMES_COMMIT}\nLicense: Apache-2.0\n",
                    encoding="utf-8",
                )
            destination.mkdir(parents=True, exist_ok=True)
            for name, target in zip(HYPERFRAMES_SKILLS, targets, strict=True):
                shutil.copytree(staged / name, target)
        return
    url, commit, _ = SOURCES[args.install]
    destination = args.destination / args.install
    if destination.exists():
        raise SystemExit(f"refusing to overwrite {destination}")
    subprocess.run(["git", "clone", "--no-checkout", url, str(destination)], check=True)
    subprocess.run(["git", "-C", str(destination), "checkout", "--detach", commit], check=True)


if __name__ == "__main__":
    main()
