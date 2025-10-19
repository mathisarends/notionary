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
[![Coverage](https://img.shields.io/badge/coverage-83%25-brightgreen)](https://github.com/yourusername/notionary)
[![Downloads](https://img.shields.io/pypi/dm/notionary?color=blue)](https://pypi.org/project/notionary/)
[![Notion API](https://img.shields.io/badge/Notion%20API-Official-000000?logo=notion&logoColor=white)](https://developers.notion.com/)

**Transform complex Notion API interactions into simple, Pythonic code.**
Perfect for developers building AI agents, automation workflows, and dynamic content systems.

</div>

---

## Why Notionary?

- **AI-Native Design** - Built specifically for AI agents with schema-driven markdown syntax
- **Smart Discovery** - Find pages and databases by name with fuzzy matching—no more hunting for IDs
- **Extended Markdown** - Rich syntax for toggles, columns, callouts, and media uploads
- **Async-First** - Modern Python with full async/await support and high performance
- **Round-Trip** - Read existing content, modify it, and write it back while preserving formatting
- **Complete Coverage** - Every Notion block type supported with type safety

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
+++
"""

await page.append_markdown(content)
```

### Complete Block Support

Every Notion block type with extended syntax:

| Block Type    | Markdown Syntax                              | Use Case                     |
| ------------- | -------------------------------------------- | ---------------------------- |
| **Toggles**   | `+++ Title\nContent\n+++`                    | Collapsible sections         |
| **Columns**   | `::: columns\n::: column\nContent\n:::\n:::` | Side-by-side layouts         |
| **Tables**    | Standard markdown tables                     | Structured data              |
| **Media**     | `[video](./file.mp4)(caption:Description)`   | Auto-uploading files         |
| **Code**      | Standard code fences with captions           | Code snippets                |
| **Equations** | `$LaTeX$`                                    | Mathematical expressions     |
| **TOC**       | `[toc]`                     | Auto-generated navigation    |

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

- Rich syntax beyond standard markdown
- Callouts, toggles, columns, media uploads
- Schema provided for AI agent integration

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

- Schema-driven syntax for LLM prompts
- Perfect for AI content generation
- Handles complex nested structures

### Complete Coverage

- Every Notion block type supported
- File uploads with automatic handling
- Database operations and properties

</td>
</tr>
</table>

---

## Examples & Documentation

### Full Documentation

[**mathisarends.github.io/notionary**](https://mathisarends.github.io/notionary/) - Complete API reference, guides, and tutorials

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
