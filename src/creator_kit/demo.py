"""Create the neutral, silent local demo without calling a provider."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .paths import job_path, write_json_new

DEMO_SOURCE = """# A local-first creator workflow\n\nThis included demo describes only this repository's workflow. It contains no external product claims.\n"""
DEMO_SPOKEN = "Make the first cut locally. Review the draft. Choose an account before any paid provider call."


def _scene_html() -> str:
    return """<!doctype html><html><head><meta charset='utf-8'><style>
*{box-sizing:border-box}body{margin:0;background:#101522;color:#f6f8ff;font-family:Arial,sans-serif;overflow:hidden}
main{height:100vh;padding:9vh 10vw;display:flex;flex-direction:column;justify-content:center;background:radial-gradient(circle at 80% 20%,#263b67 0,#101522 45%)}
.eyebrow{color:#8ddcff;font-size:2.2vw;letter-spacing:.2em;text-transform:uppercase}.title{font-size:7vw;line-height:.95;margin:3vh 0;max-width:900px}.line{height:8px;background:#8ddcff;width:var(--progress);transition:none}.note{font-size:2.2vw;color:#c7d1e9;margin-top:3vh}.card{position:absolute;right:10vw;bottom:11vh;padding:2vw;background:#17233c;border:1px solid #395882;border-radius:20px;font-size:1.7vw}
</style></head><body><main><div class='eyebrow'>Creator Workflow Kit</div><div class='title'>Make the first cut<br>locally.</div><div class='line'></div><div class='note'>Review before provider calls or publishing.</div><div class='card'>LOCAL · SILENT · REVIEW-GATED</div></main><script>
window.renderFrame=(seconds,duration)=>{document.documentElement.style.setProperty('--progress',`${Math.min(100,seconds/duration*100)}%`);document.querySelector('.title').style.transform=`translateY(${Math.sin(seconds*1.7)*5}px)`};
</script></body></html>"""


def create_demo(slug: str, *, width: int, height: int, fps: int, duration: float) -> Path:
    if width <= 0 or height <= 0 or fps <= 0 or not 8 <= duration <= 12:
        raise ValueError("demo requires positive dimensions/fps and a duration from 8 to 12 seconds")
    job = job_path(slug, create=True)
    (job / "source.md").write_text(DEMO_SOURCE, encoding="utf-8")
    (job / "spoken-script.txt").write_text(DEMO_SPOKEN + "\n", encoding="utf-8")
    (job / "article-draft.md").write_text(
        "# Draft: start locally\n\nThis deterministic sample draft is based only on `source.md`. Review before publishing.\n",
        encoding="utf-8",
    )
    (job / "post-draft.md").write_text(
        "Draft post: build a local cut, inspect it, then decide whether a provider or publisher belongs in the workflow.\n",
        encoding="utf-8",
    )
    (job / "scene.html").write_text(_scene_html(), encoding="utf-8")
    write_json_new(job / "timeline.json", {"duration_seconds": duration, "fps": fps, "seek_api": "window.renderFrame(seconds, duration)"})
    write_json_new(job / "job.json", {
        "schema_version": 1,
        "slug": slug,
        "created_at": datetime.now(UTC).isoformat(),
        "kind": "local-demo",
        "render": {"width": width, "height": height, "fps": fps, "duration_seconds": duration, "audio": "intentional-silence"},
        "provenance": {"source": "included neutral demo", "provider_calls": []},
    })
    return job


def create_prepared_job(slug: str, *, title: str, source: Path, spoken_script: Path, width: int = 1920, height: int = 1080, fps: int = 30) -> Path:
    if not title.strip() or len(title) > 120:
        raise ValueError("title must contain 1-120 characters")
    if not source.is_file() or not spoken_script.is_file():
        raise ValueError("source and spoken script must be regular files")
    source_text = source.read_text(encoding="utf-8")
    spoken_text = spoken_script.read_text(encoding="utf-8").strip()
    if not source_text.strip() or not spoken_text:
        raise ValueError("source and spoken script must not be empty")
    job = job_path(slug, create=True)
    (job / "source.md").write_text(source_text, encoding="utf-8")
    (job / "spoken-script.txt").write_text(spoken_text + "\n", encoding="utf-8")
    (job / "scene.html").write_text(_scene_html().replace("Make the first cut<br>locally.", title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")), encoding="utf-8")
    write_json_new(job / "job.json", {
        "schema_version": 1,
        "slug": slug,
        "created_at": datetime.now(UTC).isoformat(),
        "kind": "prepared-local-job",
        "render": {"width": width, "height": height, "fps": fps, "duration_seconds": None, "audio": "awaiting optional narration"},
        "provenance": {"source_name": source.name, "spoken_script_name": spoken_script.name, "provider_calls": []},
    })
    return job
