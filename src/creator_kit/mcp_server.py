"""The local MCP surface only exposes non-destructive kit operations."""

from __future__ import annotations

from .demo import create_demo
from .paths import job_path, runs_root
from .qc import qc_video
from .render import render_job


def build_server():
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("Creator Workflow Kit")

    @server.tool()
    def doctor() -> dict[str, object]:
        """Report local prerequisites without logging in or calling providers."""
        from .cli import doctor_report
        return doctor_report()

    @server.tool()
    def list_jobs() -> list[str]:
        """List job slugs under the repository-local runs directory."""
        return sorted(path.name for path in runs_root().iterdir() if path.is_dir()) if runs_root().exists() else []

    @server.tool()
    def inspect_job(slug: str) -> str:
        """Return the local job manifest for a validated slug."""
        return (job_path(slug) / "job.json").read_text(encoding="utf-8")

    @server.tool()
    def prepare_demo(slug: str = "mcp-demo") -> str:
        """Prepare, but do not render, a new local demonstration job."""
        return str(create_demo(slug, width=1920, height=1080, fps=30, duration=8))

    @server.tool()
    def render(slug: str) -> str:
        """Render an existing local job; it never calls a remote provider."""
        return str(render_job(job_path(slug)))

    return server


def main() -> None:
    build_server().run()
