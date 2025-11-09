<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./static/notionary-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="./static/notionary-light.png">
  <img alt="Notionary logo: dark mode shows a white logo, light mode shows a black logo." src="./static/browser-use.png"  width="full">
</picture>

<h1 align="center">The Modern Notion API for Python & AI Agents</h1>

<div align="center">

[![PyPI version](https://badge.fury.io/py/notionary.svg)](https://badge.fury.io/py/notionary)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/mathisarends/fc0568b66a20fbbaa5018205861c0da9/raw/notionary-coverage.json)](https://github.com/mathisarends/notionary)
[![Downloads](https://img.shields.io/pypi/dm/notionary?color=blue)](https://pypi.org/project/notionary/)
[![Documentation](https://img.shields.io/badge/docs-notionary-blue?style=flat&logo=readthedocs)](https://mathisarends.github.io/notionary/intro)
[![Notion API](https://img.shields.io/badge/Notion%20API-Official-000000?logo=notion&logoColor=white)](https://developers.notion.com/)

**Transform complex Notion API interactions into simple, Pythonic code.**
Perfect for developers building AI agents, automation workflows, and dynamic content systems.

</div>

---

## Why Notionary?

- **AI-friendly** – Composable APIs that drop cleanly into agent workflows
- **Smart discovery** – Find pages/databases by title with fuzzy matching (no ID spelunking)
- **Extended Markdown** – Toggles, columns, callouts, media, equations, tables, TOC
- **Async-first** – Modern Python with full `async` / `await`
- **Round‑trip content** – Read a page as Markdown, transform, write back
- **Full coverage** – All Notion block types with sensible defaults and type safety

---

## Installation

```bash
pip install notionary
```

Set up your [Notion integration](https://www.notion.so/profile/integrations) and configure your token:

```bash
export NOTION_SECRET=your_integration_key
```

---

## See It in Action

https://github.com/user-attachments/assets/da8b4691-bee4-4b0f-801e-dccacb630398

_Create rich database entries with properties, content, and beautiful formatting_

---

## Quick Start

### Find → Create → Update Flow

```python
from notionary import NotionPage

# Find pages by name with fuzzy matching
page = await NotionPage.from_title("Meeting Notes")

# Define rich content with extended markdown
content = """
## Action Items
- [x] Review proposal
- [ ] Schedule meeting

[callout](Key decision made! "💡")

| Task | Owner | Deadline |
|------|-------|----------|
| Design Review | Alice | 2024-03-15 |
| Implementation | Bob | 2024-03-22 |

+++ Budget Details
  See attached spreadsheet...
"""

await page.append_markdown(content)
```

Read or replace content:

```python
existing = await page.get_markdown_content()
print(existing)

await page.replace_content("# Fresh Start\nThis page was rewritten.")
```

### Complete Block Support

Every Notion block type with extended syntax:

| Block Type    | Markdown Syntax                              | Use Case                     |
| ------------- | -------------------------------------------- | ---------------------------- |
| **Toggles**   | `+++ Title\nContent\n+++`                    | Collapsible sections         |
| **Columns**   | `::: columns\n::: column\nContent\n:::\n:::` | Side-by-side layouts         |
| **Tables**    | Standard markdown tables                     | Structured data              |
| **Media**     | `[video](https://example.com/file.mp4)`      | External media URLs          |
| **Code**      | Standard code fences with captions           | Code snippets                |
| **Equations** | `$LaTeX$`                                    | Mathematical expressions     |
| **TOC**       | `[toc]`                     | Auto-generated navigation    |

---

## Architecture Overview

```mermaid
flowchart TD
  WS[Workspace] --> DB[(Database)]
  WS --> PG[Page]
  DB --> DS[(Data Source)]
  DS --> PG
  WS --> USR[Users]
  PG --> BLK[Blocks]
  PG --> CM[Comments]
  PG --> PROP[Properties]
```

---

## Key Features

<table>
<tr>
<td width="50%">

### Smart Discovery

- Find pages/databases by name
- Fuzzy matching for approximate searches
- No more hunting for IDs or URLs

### Extended Markdown

- Rich syntax beyond vanilla Markdown
- Callouts, toggles, columns, media embeds & uploads
- Fine-grained indentation + custom delimiters

### Modern Python

- Full async/await support
- Type hints throughout
- High-performance batch operations

</td>
<td width="50%">

### Round-Trip Editing

- Read existing content as markdown
- Edit and modify preserving formatting
- Write back to Notion seamlessly

### AI-Ready Architecture

- Predictable models enable prompt chaining
- Ideal for autonomous content generation
- Handles complex nested block structures

### Complete Coverage

- Every Notion block type supported
- File uploads with automatic handling
- Database operations and properties

</td>
</tr>
</table>

---

## More Examples

### Full Documentation

### Build Markdown programmatically (4-space indentation for nesting)

```python
from notionary import MarkdownBuilder

markdown = (
  MarkdownBuilder()
  .h2("Setup Guide")
  .paragraph("Basic steps.")
  .toggle("Advanced Options", lambda b:
        b.paragraph("Power user settings.")
         .bulleted_list(["Debug mode", "Custom timeouts"]))
  .columns(
    lambda c: c.paragraph("Left column"),
    lambda c: c.paragraph("Right column")
  )
  .build()
)

page = await NotionPage.from_title("Playground")
await page.append_markdown(markdown)
```

### Workspace discovery

```python
from notionary import NotionWorkspace, NotionWorkspaceQueryConfigBuilder

workspace = await NotionWorkspace.from_current_integration()
builder = NotionWorkspaceQueryConfigBuilder()
config = (
    builder
    .with_pages_only()
    .with_query("roadmap")
    .with_page_size(5)
    .build()
)
pages = await workspace.get_pages(config)
for p in pages:
    print(p.title)
```

### Data Source queries & options

```python
from notionary import NotionDataSource

ds = await NotionDataSource.from_title("Engineering Backlog")
status_labels = ds.get_status_options_by_property_name("Status")
print(status_labels)

builder = ds.get_query_builder()
params = (
    builder
    .where("Status")
    .equals("In Progress")
    .order_by_last_edited_time()
    .build()
)
pages = await ds.get_pages(query_params=params)
```

### Page property writes

```python
page = await NotionPage.from_title("Sprint Board")

await page.properties.set_select_property_by_option_name("Phase", "Design")
await page.properties.set_multi_select_property_by_option_names("Tags", ["Backend", "API"])
await page.properties.set_status_property_by_option_name("Status", "In Progress")
```

---

### Full Documentation

[**mathisarends.github.io/notionary**](https://mathisarends.github.io/notionary/) – Complete API reference, guides, and tutorials

---

## Contributing

We welcome contributions from the community! Whether you're:

- **Fixing bugs** - Help improve stability and reliability
- **Adding features** - Extend functionality for new use cases
- **Improving docs** - Make the library more accessible
- **Sharing examples** - Show creative applications and patterns

Check our [**Contributing Guide**](https://mathisarends.github.io/notionary/contributing/) to get started.

---

<div align="center">

**Ready to revolutionize your Notion workflows?**

[📖 **Read the Docs**](https://mathisarends.github.io/notionary/) • [🚀 **Getting Started**](https://mathisarends.github.io/notionary/get-started/) • [💻 **Browse Examples**](examples/)

_Built with ❤️ for Python developers and AI agents_

---

**Transform complex Notion API interactions into simple, powerful code.**

</div>
