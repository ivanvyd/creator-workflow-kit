from __future__ import annotations

from pathlib import Path
from traceback import format_exception
from urllib.error import HTTPError

import pytest

from creator_kit import paths, providers
from creator_kit.demo import create_demo, create_prepared_job
from creator_kit import render
from creator_kit.render import render_job


@pytest.fixture()
def isolated_runs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    root = tmp_path / "runs"
    monkeypatch.setattr(paths, "runs_root", lambda: root)
    return root


@pytest.mark.parametrize("slug", ["../escape", "has space", "UPPER", "a--b", "", "a/child"])
def test_slug_rejects_paths_and_malformed_values(slug: str) -> None:
    with pytest.raises(ValueError):
        paths.valid_slug(slug)


def test_demo_creates_confined_job_and_refuses_overwrite(isolated_runs: Path) -> None:
    job = create_demo("safe-job", width=320, height=180, fps=3, duration=8)
    assert job.is_relative_to(isolated_runs.resolve())
    assert (job / "scene.html").exists()
    with pytest.raises(FileExistsError):
        create_demo("safe-job", width=320, height=180, fps=3, duration=8)


def test_tts_failure_does_not_create_success_manifest(monkeypatch: pytest.MonkeyPatch, isolated_runs: Path) -> None:
    job = create_demo("voice-failure", width=320, height=180, fps=3, duration=8)
    monkeypatch.setenv("ELEVENLABS_API_KEY", "synthetic-test-key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "synthetic-test-voice")
    monkeypatch.setattr(providers, "_post_json", lambda *args: (_ for _ in ()).throw(RuntimeError("fixture network failure")))
    with pytest.raises(RuntimeError, match="fixture network failure"):
        providers.synthesize_elevenlabs(job, approve_text=True, model_id="eleven_multilingual_v2")
    assert not (job / "tts-manifest.json").exists()
    assert not (job / "narration.mp3").exists()


def test_model_call_needs_approval_before_reading_credentials(isolated_runs: Path, tmp_path: Path) -> None:
    job = create_demo("draft-approval", width=320, height=180, fps=3, duration=8)
    source = tmp_path / "source.md"
    source.write_text("synthetic source", encoding="utf-8")
    with pytest.raises(PermissionError):
        providers.draft_with_azure(job, source, approve_model_call=False)
    assert not (job / "content-manifest.json").exists()


def test_provider_failure_hides_exception_context(monkeypatch: pytest.MonkeyPatch) -> None:
    secret_marker = "synthetic-secret-marker-not-for-output"
    monkeypatch.setattr(providers, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(HTTPError("https://example.invalid/" + secret_marker, 401, "", {}, None)))
    with pytest.raises(RuntimeError) as caught:
        providers._post_json("https://example.invalid", {}, {})
    rendered = "".join(format_exception(caught.type, caught.value, caught.tb))
    assert secret_marker not in rendered


def test_missing_writer_deployment_stops_before_provider_call(monkeypatch: pytest.MonkeyPatch, isolated_runs: Path, tmp_path: Path) -> None:
    job = create_demo("missing-writer", width=320, height=180, fps=3, duration=8)
    source = tmp_path / "source.md"
    source.write_text("synthetic source", encoding="utf-8")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://synthetic.invalid")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "synthetic-test-key")
    monkeypatch.setenv("AZURE_OPENAI_REVIEWER_DEPLOYMENT", "reviewer")
    calls: list[object] = []
    monkeypatch.setattr(providers, "_chat", lambda *args: calls.append(args) or "unexpected")
    with pytest.raises(RuntimeError, match="configured writer/reviewer"):
        providers.draft_with_azure(job, source, approve_model_call=True)
    assert calls == []


def test_prepared_job_recovers_after_narration_is_added(monkeypatch: pytest.MonkeyPatch, isolated_runs: Path, tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    spoken = tmp_path / "spoken.txt"
    source.write_text("source", encoding="utf-8")
    spoken.write_text("spoken", encoding="utf-8")
    job = create_prepared_job("prepared-job", title="Local title", source=source, spoken_script=spoken)
    with pytest.raises(RuntimeError, match="need narration"):
        render_job(job)
    assert not (job / "frames").exists()
    narration = job / "narration.mp3"
    narration.write_bytes(b"synthetic audio fixture")
    monkeypatch.setattr(render, "_audio_duration", lambda path: 1.0)
    monkeypatch.setattr(render, "_capture_frames", lambda *args, **kwargs: None)

    def fake_encode(command: list[str]) -> None:
        Path(command[-1]).write_bytes(b"synthetic video fixture")

    monkeypatch.setattr(render, "_run", fake_encode)
    output = render_job(job)
    assert output.exists()
    assert (job / "render-manifest.json").exists()
