<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./static/notionary-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="./static/notionary-light.png">
  <img alt="Notionary logo: dark mode shows a white logo, light mode shows a black logo." src="./static/browser-use.png"  width="full">
</picture>

<h1 align="center">The Modern Notion API for Python & AI Agents</h1>

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-mathisarends.github.io-blue.svg)](https://mathisarends.github.io/notionary/)

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

### Creating Rich Database Entries

https://github.com/user-attachments/assets/da8b4691-bee4-4b0f-801e-dccacb630398

*Create styled project pages with properties, content, and rich formatting*

### Local File Uploads (Videos & Images)

https://github.com/user-attachments/assets/a079ec01-bb56-4c65-8260-7b1fca42ac68

*Upload videos and images using simple markdown syntax - files are automatically uploaded to Notion*

---

## Quick Start

### Find → Create → Update Flow

```python
import asyncio
from notionary import NotionPage, NotionDatabase

async def main():
    # Find pages by name - fuzzy matching included!
    page = await NotionPage.from_page_name("Meeting Notes")

    # Option 1: Direct Extended Markdown
    await page.append_markdown("""
    ## Action Items
    - [x] Review project proposal
    - [ ] Schedule team meeting
    - [ ] Update documentation

    [callout](Meeting decisions require follow-up "💡")

    +++ Details
    Additional context and next steps...
    +++
    """)

    # Option 2: Type-Safe Builder (maps to same markdown internally)
    await page.append_markdown(lambda builder: (
        builder
        .h2("Project Status")
        .callout("Milestone reached!", "🎉")
        .columns(
            lambda col: col.h3("Completed").bulleted_list([
                "API design", "Database setup", "Authentication"
            ]),
            lambda col: col.h3("In Progress").bulleted_list([
                "Frontend UI", "Testing", "Documentation"
            ]),
            width_ratios=[0.6, 0.4]
        )
        .toggle("Budget Details", lambda t: t
            .table(["Item", "Cost", "Status"], [
                ["Development", "$15,000", "Paid"],
                ["Design", "$8,000", "Pending"]
            ])
        )
    ))

asyncio.run(main())
```

### Complete Block Support

Every Notion block type with extended syntax:

| Block Type | Markdown Syntax | Use Case |
|------------|-----------------|----------|
| **Callouts** | `[callout](Text "🔥")` | Highlighting key information |
| **Toggles** | `+++ Title\nContent\n+++` | Collapsible sections |
| **Columns** | `::: columns\n::: column\nContent\n:::\n:::` | Side-by-side layouts |
| **Tables** | Standard markdown tables | Structured data |
| **Media** | `[video](./file.mp4)(caption:Description)` | Auto-uploading files |
| **Code** | Standard code fences with captions | Code snippets |
| **Equations** | `$LaTeX$` | Mathematical expressions |
| **TOC** | `[toc](blue_background)` | Auto-generated navigation |

---

## What You Can Build 💡

### **AI Content Systems**
- **Report Generation**: AI agents that create structured reports, documentation, and analysis
- **Content Pipelines**: Automated workflows that process data and generate Notion pages
- **Knowledge Management**: AI-powered documentation systems with smart categorization

### **Workflow Automation**
- **Project Management**: Sync project status, update timelines, generate progress reports
- **Data Integration**: Connect external APIs and databases to Notion workspaces
- **Template Systems**: Dynamic page generation from templates and data sources

### **Content Management**
- **Bulk Operations**: Mass page updates, content migration, and database management
- **Media Handling**: Automated image/video uploads with proper organization
- **Cross-Platform**: Sync content between Notion and other platforms

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

### Quick Links
- [**Getting Started**](https://mathisarends.github.io/notionary/get-started/) - Setup and first steps
- [**Page Management**](https://mathisarends.github.io/notionary/page/) - Content and properties
- [**Database Operations**](https://mathisarends.github.io/notionary/database/) - Queries and management
- [**Block Types Reference**](https://mathisarends.github.io/notionary/blocks/) - Complete syntax guide

### Hands-On Examples

**Core Functionality:**
- [Page Management](examples/page_example.py) - Create, update, and manage pages
- [Database Operations](examples/database.py) - Connect and query databases
- [Workspace Discovery](examples/workspace_discovery.py) - Explore your workspace

**Extended Markdown:**
- [Basic Formatting](examples/markdown/basic.py) - Text, lists, and links
- [Callouts & Highlights](examples/markdown/callout.py) - Information boxes
- [Toggle Sections](examples/markdown/toggle.py) - Collapsible content
- [Multi-Column Layouts](examples/markdown/columns.py) - Side-by-side design
- [Tables & Data](examples/markdown/table.py) - Structured presentations

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

*Built with ❤️ for Python developers and AI agents*

---

**Transform complex Notion API interactions into simple, powerful code.**

</div>
