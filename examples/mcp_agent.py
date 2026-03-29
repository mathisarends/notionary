"""Use the Notionary MCP server with the OpenAI Agents SDK.

Prerequisites:
    pip install notionary[mcp]

Environment variables:
    NOTION_API_KEY
    OPENAI_API_KEY
"""

import asyncio
import os
import sys

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv(override=True)


async def main():
    async with MCPServerStdio(
        name="Notionary",
        params={
            "command": sys.executable,
            "args": ["-m", "notionary.mcp.server"],
            "env": {
                **os.environ,
                "NOTION_API_KEY": os.environ["NOTION_API_KEY"],
            },
        },
        client_session_timeout_seconds=30,
    ) as server:
        agent = Agent(
            name="Notion Assistant",
            instructions=(
                "You help users manage their Notion workspace. "
                "Use the available tools to search, read, create, and edit pages, "
                "databases, and data sources. "
                "When presenting results, be concise and well-structured."
            ),
            mcp_servers=[server],
        )

        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])
        else:
            query = "Search my workspace and list what you find."

        result = await Runner.run(agent, query)
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
