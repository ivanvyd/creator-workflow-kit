"""Small delivery checks for silent local-first demo video."""

from __future__ import annotations

import json
import subprocess
from fractions import Fraction
from pathlib import Path


def _command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True)


def qc_video(path: Path, *, expected_width: int | None = None, expected_height: int | None = None, expected_fps: int | None = None) -> dict[str, object]:
    job_path = path.parent / "job.json"
    expected_duration: float | None = None
    if job_path.exists():
        job = json.loads(job_path.read_text(encoding="utf-8"))
        render = job.get("render", {})
        expected_width = expected_width or render.get("width")
        expected_height = expected_height or render.get("height")
        expected_fps = expected_fps or render.get("fps")
        expected_duration = render.get("duration_seconds")
    probe = _command(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", str(path)])
    if probe.returncode:
        raise RuntimeError(probe.stderr.strip())
    data = json.loads(probe.stdout)
    video = next(stream for stream in data["streams"] if stream["codec_type"] == "video")
    fps = float(Fraction(video["r_frame_rate"]))
    manifest_path = path.parent / "render-manifest.json"
    expected_audio = "intentional-silence"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_audio = manifest.get("audio", expected_audio)
        manifest_fps = manifest.get("fps")
        manifest_duration = manifest.get("duration_seconds")
        if isinstance(manifest_fps, int) and manifest_fps > 0:
            expected_fps = manifest_fps
        if isinstance(manifest_duration, (int, float)) and manifest_duration > 0:
            expected_duration = float(manifest_duration)
    has_audio = any(stream["codec_type"] == "audio" for stream in data["streams"])
    checks = {
        "has_video": True,
        "progressive": video.get("field_order") in {"progressive", "unknown"},
        "h264_yuv420p": video.get("codec_name") == "h264" and video.get("pix_fmt") == "yuv420p",
        "expected_dimensions": expected_width is None or (video["width"], video["height"]) == (expected_width, expected_height),
        "expected_fps": expected_fps is None or abs(fps - expected_fps) < 0.001,
        "audio_expectation": has_audio if expected_audio == "narration" else not has_audio,
        "full_decode": False,
    }
    actual_duration = float(data["format"]["duration"])
    expected_frames = round(float(expected_duration) * expected_fps) if expected_duration is not None and expected_fps is not None else None
    checks["expected_frame_count"] = expected_frames is None or int(video.get("nb_read_frames", 0)) == expected_frames
    checks["expected_duration"] = expected_duration is None or abs(actual_duration - float(expected_duration)) < 0.05
    decode = _command(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"])
    checks["full_decode"] = decode.returncode == 0
    return {"path": str(path), "fps": fps, "frames": int(video.get("nb_read_frames", 0)), "duration_seconds": actual_duration, "audio": expected_audio, "checks": checks}
