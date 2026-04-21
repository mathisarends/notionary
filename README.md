<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./static/notionary-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="./static/notionary-light.png">
  <img alt="Notionary logo" src="./static/notionary-light.png" width="full">
</picture>

<h1 align="center">Notionary</h1>

<div align="center">

[![PyPI version](https://badge.fury.io/py/notionary.svg)](https://badge.fury.io/py/notionary)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/notionary)](https://pypi.org/project/notionary/)
[![Documentation](https://img.shields.io/badge/docs-notionary-blue?style=flat&logo=readthedocs)](https://mathisarends.github.io/notionary)
[![Notion API](https://img.shields.io/badge/Notion%20API-v1-black?logo=notion)](https://developers.notion.com/)

**The Modern Notion API for Python & AI Agents**

Transform complex Notion API interactions into simple, Pythonic code. Perfect for developers building AI agents, automation workflows, and dynamic content systems.

</div>

---

## Why Notionary?

|                        |                                                                       |
| ---------------------- | --------------------------------------------------------------------- |
| **AI-friendly**        | Composable APIs that drop cleanly into agent workflows                |
| **Smart discovery**    | Find pages/databases by title with fuzzy matching — no ID spelunking  |
| **Markdown content**   | Read & write page content as Markdown via the Notion Markdown API     |
| **Async-first**        | Modern Python with full `async` / `await`                             |
| **Round-trip editing** | Read a page as Markdown, transform it, write it back                  |
| **Full coverage**      | Pages, databases, data sources, file uploads, users, workspace search |

---

## Installation

```bash
pip install notionary
```

Set your Notion integration token:

```bash
export NOTION_API_KEY=your_integration_key
```

---

## Quick Start

All access goes through the `Notionary` client, which exposes namespace objects — each mapping to a Notion API area.

```python
import asyncio
from notionary import Notionary

async def main():
    async with Notionary() as notion:
        # Find a page by title (fuzzy matching)
        page = await notion.pages.find("Meeting Notes")
        print(page.title, page.url)

        # Read content as Markdown
        md = await page.get_markdown()
        print(md)

        # Append content
        await page.append("## Action Items\n- [ ] Review proposal")

        # Replace all content
        await page.replace("# Fresh Start\nThis page was rewritten.")

asyncio.run(main())
```

---

## Core API

### Pages

```python
async with Notionary() as notion:
    # Lookup
    page = await notion.pages.find("Sprint Board")
    page = await notion.pages.from_id(page_uuid)

    # List & search
    pages = await notion.pages.list(query="roadmap")
```

#### Content (Markdown API)

```python
    md = await page.get_markdown()       # read as Markdown
    await page.append("## New Section") # append blocks
    await page.replace("# Replaced")   # overwrite all content
    await page.clear()                  # remove all blocks
```

#### Metadata

```python
    await page.rename("New Title")
    await page.set_icon("🚀")
    await page.set_cover("https://example.com/cover.png")
    await page.random_cover()
```

#### Properties

```python
    # Set a single property (type-validated against the schema)
    await page.set_property("Status", "Done")
    await page.set_property("Due Date", "2025-12-31")
    await page.set_property("Priority", 3)
    await page.set_property("Archived", True)
    await page.set_property("Tags", ["backend", "urgent"])

    # Set multiple properties in one API call
    await page.set_properties({
        "Status": "In Progress",
        "Due Date": "2025-12-31",
        "Priority": 2,
    })

    # Inspect the property schema (types, current values, valid options)
    schema = await page.describe_properties()
    # schema["Status"] → PagePropertyDescription(type="status", current="Todo", options=["Todo", "In Progress", "Done"])
```

Supported property types: `checkbox`, `date`, `email`, `multi_select`, `number`, `phone_number`, `rich_text`, `select`, `status`, `title`, `url`, `relation`.

For **relation** properties on data-source pages, you can pass a page ID (UUID string) or a page title — the title is automatically resolved to an ID:

```python
    # By page ID
    await page.set_property("Project", "abc123...")
    # By title (auto-resolved via the related data source)
    await page.set_property("Project", "Quarterly Review")
```

#### Comments & Lifecycle

```python
    await page.comment("Review completed")
    await page.lock()
    await page.trash()
```

> **Notion API Reference:** [Pages](https://developers.notion.com/reference/page) · [Markdown](https://developers.notion.com/reference/markdown)

---

### Databases

```python
async with Notionary() as notion:
    # Lookup
    db = await notion.databases.find("Tasks")
    db = await notion.databases.from_id(db_uuid)

    # Create
    db = await notion.databases.create(
        parent_page_id=page_uuid,
        title="New Database",
        icon_emoji="📊",
    )

    # Metadata
    await db.set_title("Project Tracker")
    await db.set_description("All current projects")
    await db.set_icon("📊")
    await db.lock()
```

> **Notion API Reference:** [Databases](https://developers.notion.com/reference/database)

---

### Data Sources

Data sources represent queryable Notion databases with schema awareness — useful for building structured content pipelines.

```python
async with Notionary() as notion:
    ds = await notion.data_sources.find("Engineering Backlog")

    # Schema introspection — property types, current options, and relation pages
    schema = await ds.describe_properties()
    # schema["Status"] → DataSourcePropertyDescription(type="status", options=["Todo", "In Progress", "Done"])
    # schema["Assignee"] → DataSourcePropertyDescription(type="relation", relation_options=[...])

    # Create a page inside the data source
    page = await ds.create_page(title="New Feature")

    # Query with filters
    results = await ds.query(filter={"property": "Status", "select": {"equals": "In Progress"}})

    # Metadata
    await ds.set_title("Sprint Board")
    await ds.set_icon("🧭")
```

> **Notion API Reference:** [Data Sources](https://developers.notion.com/reference/post-database-query)

---

### File Uploads

```python
from pathlib import Path

async with Notionary() as notion:
    # Upload from disk
    result = await notion.file_uploads.upload(Path("./report.pdf"))

    # Upload from bytes (e.g. generated images, in-memory content)
    result = await notion.file_uploads.upload_from_bytes(
        content=image_bytes,
        filename="chart.png",
    )

    # List previous uploads
    uploads = await notion.file_uploads.list()
```

---

### Users

```python
async with Notionary() as notion:
    all_users = await notion.users.list()
    people    = await notion.users.list(filter="person")
    bots      = await notion.users.list(filter="bot")
    me        = await notion.users.me()

    matches   = await notion.users.search("alex")
```

---

### Workspace Search

```python
async with Notionary() as notion:
    results = await notion.workspace.search(query="roadmap")
    for r in results:
        print(type(r).__name__, r.title)
```

---

## Key Features

### Smart Discovery

- Find pages and databases by human-readable name
- Fuzzy matching handles typos and partial titles
- No more hunting for opaque IDs or copying page URLs

### Markdown Content API

- Read any Notion page as clean Markdown
- Append or replace blocks using Markdown syntax
- Powered by the official [Notion Markdown API](https://developers.notion.com/reference/markdown)

### Round-Trip Editing

```python
# Read → transform → write back
md = await page.get_markdown()
updated = md.replace("Draft", "Final")
await page.replace(updated)
```

### Modern Python

- Full `async` / `await` support throughout
- Type hints on all public APIs
- Pydantic models for all API responses
- Context-manager client for clean resource handling

### AI-Ready Architecture

- Namespace-based API maps naturally to agent tool sets
- Predictable response models enable prompt chaining
- Works with LangChain, LlamaIndex, OpenAI Agents SDK, Claude, and custom agent runtimes

---

## Contributing

Contributions are welcome — whether you're fixing bugs, adding features, improving docs, or sharing examples.
Check the [Contributing Guide](CONTRIBUTING.md) to get started.

---

## Documentation

[**mathisarends.github.io/notionary**](https://mathisarends.github.io/notionary/) — Complete API reference auto-generated from source.

---

<div align="center">
Built with ❤️ for Python developers and AI agents
</div>
