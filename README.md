<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./static/notionary-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="./static/notionary-light.png">
  <img alt="Notionary logo" src="./static/browser-use.png" width="full">
</picture>

<h1 align="center">Notionary</h1>

<div align="center">

[![PyPI version](https://badge.fury.io/py/notionary.svg)](https://badge.fury.io/py/notionary)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-notionary-blue?style=flat&logo=readthedocs)](https://mathisarends.github.io/notionary)

**Python library and MCP server for managing Notion workspaces programmatically.**

</div>

---

## Installation

```bash
pip install notionary          # core library
pip install notionary[mcp]     # + MCP server
```

Set your integration token:

```bash
export NOTION_API_KEY=your_integration_key
```

---

## Quick Start

```python
import asyncio
from notionary import Notionary

async def main():
    async with Notionary() as notion:
        page = await notion.pages.find("Meeting Notes")
        md = await page.get_markdown()
        await page.append("## Action Items\n- [ ] Review proposal")

asyncio.run(main())
```

---

## MCP Server

Notionary ships a built-in [Model Context Protocol](https://modelcontextprotocol.io/) server that lets any MCP-compatible AI agent manage your Notion workspace.

### Claude Desktop / Claude Code

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

### OpenAI Agents SDK

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
import sys

async def main():
    async with MCPServerStdio(
        name="Notionary",
        params={"command": sys.executable, "args": ["-m", "notionary.mcp.server"]},
    ) as server:
        agent = Agent(
            name="Notion Assistant",
            instructions="You help users manage their Notion workspace.",
            mcp_servers=[server],
        )
        result = await Runner.run(agent, "Search my workspace and list what you find.")
        print(result.final_output)
```

### Available MCP Tools

| Area | Tools |
|------|-------|
| **Workspace** | `search_workspace` |
| **Pages** | `list_pages`, `find_page`, `get_page_content`, `get_page_comments`, `update_page`, `append_to_page`, `replace_page_content`, `clear_page`, `comment_on_page`, `rename_page`, `set_page_property`, `trash_page`, `restore_page`, `lock_page`, `unlock_page` |
| **Data Sources** | `list_data_sources`, `find_data_source`, `get_data_source_schema`, `create_page_in_data_source`, `update_data_source`, `list_data_source_templates`, `trash_data_source`, `restore_data_source` |
| **Databases** | `list_databases`, `find_database`, `create_database`, `update_database`, `trash_database`, `restore_database` |
| **Users** | `list_users`, `search_users`, `get_me` |

---

## Documentation

[**mathisarends.github.io/notionary**](https://mathisarends.github.io/notionary/) — Full API reference and guides.
