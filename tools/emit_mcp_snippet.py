"""Print copy-paste configuration snippets without changing agent settings."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    executable = root / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    command = str(executable)
    toml_command = command.replace("\\", "\\\\")
    print("Codex config.toml:")
    print(f'[mcp_servers.creator-workflow-kit]\ncommand = "{toml_command}"\nargs = ["-m", "creator_kit", "mcp"]')
    print("\nClaude Desktop JSON:")
    print(json.dumps({"mcpServers": {"creator-workflow-kit": {"command": command, "args": ["-m", "creator_kit", "mcp"]}}}, indent=2))
    print("\nRemote catalog: mcp/catalog.json. Add hosted OAuth servers through your client UI; this script never edits global settings.")


if __name__ == "__main__":
    main()
