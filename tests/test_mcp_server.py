from __future__ import annotations

from creator_kit.mcp_server import build_server


def test_local_mcp_declares_the_non_destructive_tools() -> None:
    server = build_server()
    names = {tool.name for tool in server._tool_manager.list_tools()}
    assert {"doctor", "list_jobs", "inspect_job", "prepare_demo", "render"} <= names
