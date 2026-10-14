"""Command-line entry point for the portable, local-first creator kit."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

from .config import load_config
from .demo import create_demo, create_prepared_job
from .paths import job_path, read_json, runs_root, valid_slug
from .providers import draft_with_azure, synthesize_elevenlabs
from .qc import qc_video
from .render import render_job
from .youtube import authorize_readonly, channel_report, write_report


def doctor_report() -> dict[str, object]:
    config = load_config()
    azure = config["azure_openai"]
    writer_env = str(azure["writer_deployment_env"])
    reviewer_env = str(azure["reviewer_deployment_env"])
    return {
        "python": sys.version.split()[0],
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "ffprobe": bool(shutil.which("ffprobe")),
        "playwright_package": importlib.util.find_spec("playwright") is not None,
        "mcp_package": importlib.util.find_spec("mcp") is not None,
        "runs_directory": str(runs_root()),
        "providers": {
            "elevenlabs_direct_api_configured": all(bool(os.environ.get(name)) for name in ("ELEVENLABS_API_KEY", "ELEVENLABS_VOICE_ID")),
            "azure_openai_writer_configured": all(bool(os.environ.get(name)) for name in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", writer_env)),
            "azure_openai_reviewer_configured": all(bool(os.environ.get(name)) for name in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", reviewer_env)),
            "youtube": "read-only OAuth is an explicit separate command",
            "heygen": "remote MCP OAuth only; see mcp/catalog.json",
        },
        "doctor_did_not": ["log in", "call a provider", "create a token", "modify configuration"],
    }


def _job_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("slug", type=valid_slug)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="creator-kit", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    plan = sub.add_parser("plan", help="print the local-first stages without creating files")
    demo = sub.add_parser("demo", help="create and render a provider-free local demo")
    demo.add_argument("--slug", default="hello-creator", type=valid_slug)
    demo.add_argument("--width", type=int, default=1920)
    demo.add_argument("--height", type=int, default=1080)
    demo.add_argument("--fps", type=int, default=30)
    demo.add_argument("--duration", type=float, default=8)
    prepare = sub.add_parser("prepare", help="create an unrendered local job from supplied source and spoken script")
    _job_arg(prepare)
    prepare.add_argument("--title", required=True)
    prepare.add_argument("--source", type=Path, required=True)
    prepare.add_argument("--spoken-script", type=Path, required=True)
    render = sub.add_parser("render")
    _job_arg(render)
    qc = sub.add_parser("qc")
    qc.add_argument("video", type=Path)
    tts = sub.add_parser("tts", help="direct ElevenLabs API; requires reviewed text approval")
    _job_arg(tts); tts.add_argument("--approve-text", action="store_true"); tts.add_argument("--model"); tts.add_argument("--language-code")
    draft = sub.add_parser("content-draft", help="Azure-compatible draft call; never publishes")
    _job_arg(draft); draft.add_argument("--source", type=Path, required=True); draft.add_argument("--kind", choices=("article", "post"), default="article"); draft.add_argument("--approve-model-call", action="store_true")
    auth = sub.add_parser("youtube-auth", help="create a dedicated read-only YouTube OAuth token")
    auth.add_argument("--credentials", type=Path, required=True); auth.add_argument("--token", type=Path, required=True)
    report = sub.add_parser("youtube-report", help="fetch a read-only channel report into an existing job")
    _job_arg(report); report.add_argument("--token", type=Path, required=True)
    sub.add_parser("mcp", help="run the local MCP server over stdio")
    args = parser.parse_args(argv)
    if args.command == "doctor":
        print(json.dumps(doctor_report(), indent=2)); return
    if args.command == "plan":
        print("plan → demo or prepare job → render → qc → optional reviewed provider calls → manual publish decision"); return
    if args.command == "demo":
        job = create_demo(args.slug, width=args.width, height=args.height, fps=args.fps, duration=args.duration)
        video = render_job(job)
        print(video); return
    if args.command == "prepare":
        print(create_prepared_job(args.slug, title=args.title, source=args.source, spoken_script=args.spoken_script)); return
    if args.command == "render":
        print(render_job(job_path(args.slug))); return
    if args.command == "qc":
        report = qc_video(args.video)
        print(json.dumps(report, indent=2))
        if not all(report["checks"].values()):
            raise SystemExit(1)
        return
    if args.command == "tts":
        print(synthesize_elevenlabs(job_path(args.slug), approve_text=args.approve_text, model_id=args.model, language_code=args.language_code)); return
    if args.command == "content-draft":
        print(draft_with_azure(job_path(args.slug), args.source, approve_model_call=args.approve_model_call, kind=args.kind)); return
    if args.command == "youtube-auth":
        authorize_readonly(args.credentials, args.token); print(args.token); return
    if args.command == "youtube-report":
        print(write_report(job_path(args.slug), channel_report(args.token))); return
    if args.command == "mcp":
        from .mcp_server import main as mcp_main
        mcp_main(); return
    raise AssertionError(f"unhandled command {args.command}")
