from __future__ import annotations

from pathlib import Path
import json
import subprocess

import pytest

from creator_kit.cli import main
from creator_kit.qc import qc_video


def test_qc_accepts_a_small_silent_h264_fixture(tmp_path: Path) -> None:
    # The test fixture is intentionally created offline by FFmpeg; it contains no personal media.
    video = tmp_path / "synthetic.mp4"
    result = subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=blue:s=64x64:r=3:d=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report = qc_video(video, expected_width=64, expected_height=64, expected_fps=3)
    assert all(report["checks"].values())


def test_qc_cli_returns_failure_for_a_failed_expectation(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    video = tmp_path / "synthetic.mp4"
    result = subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=blue:s=64x64:r=30:d=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    (tmp_path / "job.json").write_text(json.dumps({"render": {"width": 64, "height": 64, "fps": 29, "duration_seconds": 1}}), encoding="utf-8")
    with pytest.raises(SystemExit, match="1"):
        main(["qc", str(video)])
    assert '"expected_fps": false' in capsys.readouterr().out


def test_qc_uses_render_manifest_for_narration_duration_and_fps(tmp_path: Path) -> None:
    video = tmp_path / "synthetic.mp4"
    result = subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=blue:s=64x64:r=30:d=1", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(video)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    (tmp_path / "job.json").write_text(json.dumps({"render": {"width": 64, "height": 64, "fps": 30, "duration_seconds": None}}), encoding="utf-8")
    (tmp_path / "render-manifest.json").write_text(json.dumps({"audio": "narration", "fps": 30, "duration_seconds": 1.0}), encoding="utf-8")
    report = qc_video(video)
    assert report["checks"]["expected_fps"]
    assert report["checks"]["expected_frame_count"]
    assert report["checks"]["expected_duration"]
    assert report["checks"]["audio_expectation"]
