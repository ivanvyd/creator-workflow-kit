from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


def _tool(name: str):
    path = Path(__file__).resolve().parents[1] / "tools" / f"{name}.py"
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_sensitive_scan_skips_installed_dependencies_and_render_output(tmp_path: Path) -> None:
    scanner = _tool("scan_sensitive")
    marker = "gh" + "p_" + "a" * 24
    (tmp_path / "example.md").write_text("English example", encoding="utf-8")
    for skipped in ("node_modules", "renders", ".hyperframes"):
        directory = tmp_path / skipped
        directory.mkdir()
        (directory / "ignored.txt").write_text(marker, encoding="utf-8")
    assert scanner.scan(tmp_path) == []


def test_hyperframes_skill_installer_copies_selected_skills_with_license_and_provenance(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    installer = _tool("install_upstream_skills")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(installer, "ROOT", tmp_path)

    def fake_run(command: list[str], check: bool) -> subprocess.CompletedProcess[str]:
        if command[1] == "clone":
            checkout = Path(command[-1])
            checkout.mkdir(parents=True)
            return subprocess.CompletedProcess(command, 0)
        checkout = Path(command[2])
        (checkout / "LICENSE").write_text("Apache-2.0 fixture", encoding="utf-8")
        (checkout / "NOTICE").write_text("notice fixture", encoding="utf-8")
        for name in installer.HYPERFRAMES_SKILLS:
            source = checkout / "skills" / name
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text(f"# {name}", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(installer.subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["install_upstream_skills.py", "--install-hyperframes-skills", "--destination", ".agents/skills"])
    installer.main()
    for name in installer.HYPERFRAMES_SKILLS:
        skill = tmp_path / ".agents" / "skills" / name
        assert (skill / "SKILL.md").exists()
        assert (skill / "LICENSE").read_text(encoding="utf-8") == "Apache-2.0 fixture"
        assert (skill / "NOTICE").read_text(encoding="utf-8") == "notice fixture"
        assert installer.HYPERFRAMES_COMMIT in (skill / "UPSTREAM_PROVENANCE.md").read_text(encoding="utf-8")


def test_hyperframes_skill_installer_refuses_an_existing_target(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    installer = _tool("install_upstream_skills")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(installer, "ROOT", tmp_path)
    target = tmp_path / ".agents" / "skills" / "hyperframes-core"
    target.mkdir(parents=True)
    (target / "keep.txt").write_text("preserve", encoding="utf-8")
    monkeypatch.setattr(installer.subprocess, "run", lambda *args, **kwargs: pytest.fail("clone must not run when a target exists"))
    monkeypatch.setattr(sys, "argv", ["install_upstream_skills.py", "--install-hyperframes-skills", "--destination", ".agents/skills"])
    with pytest.raises(SystemExit, match="refusing to overwrite"):
        installer.main()
    assert (target / "keep.txt").read_text(encoding="utf-8") == "preserve"


def test_hyperframes_skill_installer_refuses_external_cwd_before_clone(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    installer = _tool("install_upstream_skills")
    external = tmp_path / "external"
    external.mkdir()
    monkeypatch.chdir(external)
    monkeypatch.setattr(installer, "ROOT", tmp_path / "kit")
    monkeypatch.setattr(installer.subprocess, "run", lambda *args, **kwargs: pytest.fail("clone must not run outside the kit root"))
    monkeypatch.setattr(sys, "argv", ["install_upstream_skills.py", "--install-hyperframes-skills", "--destination", ".agents/skills"])
    with pytest.raises(SystemExit, match="inside the current repository"):
        installer.main()
