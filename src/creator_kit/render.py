"""Deterministic seek-and-capture renderer for included HTML scenes."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

from .paths import confined, read_json, write_json_new


def _run(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"render command failed: {result.stderr[-1500:]}")


def _audio_duration(path: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("could not measure narration audio")
    return float(result.stdout.strip())


def _capture_frames(scene: str, frames: Path, *, width: int, height: int, fps: int, duration: float, frame_count: int) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(scene, wait_until="load")
        page.wait_for_function("() => typeof window.renderFrame === 'function'")
        for index in range(frame_count):
            page.evaluate("([t, d]) => window.renderFrame(t, d)", [index / fps, duration])
            page.screenshot(path=str(frames / f"{index:05d}.png"))
        browser.close()


def render_job(job: Path) -> Path:
    metadata = read_json(job / "job.json")
    render = metadata["render"]
    assert isinstance(render, dict)
    output = job / "demo.mp4"
    frames = confined(job, job / "frames")
    if output.exists() or frames.exists():
        raise FileExistsError("render outputs already exist; use a new job slug instead")
    width, height = int(render["width"]), int(render["height"])
    fps = int(render["fps"])
    narration = job / "narration.mp3"
    if narration.exists():
        duration = _audio_duration(narration)
    elif render["duration_seconds"] is not None:
        duration = float(render["duration_seconds"])
    else:
        raise RuntimeError("prepared jobs need narration.mp3 before rendering, or create a local demo with an explicit duration")
    frame_count = round(fps * duration)
    scene = (job / "scene.html").resolve().as_uri()
    frames_created = False
    output_created = False
    try:
        frames.mkdir()
        frames_created = True
        _capture_frames(scene, frames, width=width, height=height, fps=fps, duration=duration, frame_count=frame_count)
        encode = ["ffmpeg", "-y", "-framerate", str(fps), "-i", str(frames / "%05d.png")]
        if narration.exists():
            encode.extend(["-i", str(narration), "-c:a", "aac", "-b:a", "192k", "-shortest"])
        encode.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)])
        output_created = True
        _run(encode)
        write_json_new(job / "render-manifest.json", {"output": output.name, "duration_seconds": duration, "fps": fps, "audio": "narration" if narration.exists() else "intentional-silence"})
    except Exception:
        if output_created and output.exists():
            output.unlink()
        if frames_created and frames.exists() and frames.parent.resolve() == job.resolve():
            shutil.rmtree(frames)
        raise
    return output
