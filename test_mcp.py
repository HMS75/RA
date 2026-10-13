"""Starts the MCP server and talks to it like an MCP app would: lists the tools, calls one."""
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print(f"Server exposes {len(tools.tools)} tools:\n")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description.splitlines()[0]}")

            print("\nCalling database_overview ...")
            result = await session.call_tool("database_overview", {})
            print(result.content[0].text)


asyncio.run(main())