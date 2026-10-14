from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_local_mcp_initializes_lists_and_calls_doctor() -> None:
    async def probe() -> None:
        root = Path(__file__).resolve().parents[1]
        parameters = StdioServerParameters(command=sys.executable, args=["-m", "creator_kit", "mcp"], cwd=str(root))
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert "doctor" in {tool.name for tool in tools.tools}
                result = await session.call_tool("doctor", {})
                assert not result.isError
    asyncio.run(probe())
