# MCP Server

Notionary includes a built-in [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that exposes your Notion workspace to AI agents. Any MCP-compatible client — the OpenAI Agents SDK, Claude Desktop, Claude Code, or others — can use it out of the box.

## Installation

```bash
pip install notionary[mcp]
```

## Available Tools

| Area | Tools |
|------|-------|
| **Workspace** | `search_workspace` |
| **Pages** | `list_pages`, `find_page`, `get_page_content`, `get_page_comments`, `update_page`, `append_to_page`, `replace_page_content`, `clear_page`, `comment_on_page`, `rename_page`, `set_page_property`, `trash_page`, `restore_page`, `lock_page`, `unlock_page` |
| **Data Sources** | `list_data_sources`, `find_data_source`, `get_data_source_schema`, `create_page_in_data_source`, `update_data_source`, `list_data_source_templates`, `trash_data_source`, `restore_data_source` |
| **Databases** | `list_databases`, `find_database`, `create_database`, `update_database`, `trash_database`, `restore_database` |
| **Users** | `list_users`, `search_users`, `get_me` |

## Usage with the OpenAI Agents SDK

```python
import asyncio
import os
import sys

from agents import Agent, Runner
from agents.mcp import MCPServerStdio


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
            instructions="You help users manage their Notion workspace.",
            mcp_servers=[server],
        )

        result = await Runner.run(agent, "Search my workspace and list what you find.")
        print(result.final_output)


asyncio.run(main())
```

!!! note "Environment variables"
    The MCP stdio transport does **not** inherit environment variables automatically.
    Pass `NOTION_API_KEY` explicitly via the `env` parameter as shown above.

## Usage with Claude Desktop / Claude Code

Add this to your MCP configuration:

```json
{
  "mcpServers": {
    "notionary": {
      "command": "notionary-mcp",
      "env": {
        "NOTION_API_KEY": "your_integration_key"
      }
    }
  }
}
```

## Running the server standalone

```bash
# Via the entry point
notionary-mcp

# Or as a module
python -m notionary.mcp.server
```

The server starts in **stdio** mode by default, which is what MCP clients expect.
