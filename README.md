<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./static/notionary-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="./static/notionary-light.png">
  <img alt="Notionary logo: dark mode shows a white logo, light mode shows a black logo." src="./static/browser-use.png"  width="full">
</picture>

<h1 align="center">Notion API simplified for Python developers 🐍</h1>

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-mathisarends.github.io-blue.svg)](https://mathisarends.github.io/notionary/)

Transform complex Notion API interactions into simple, Pythonic code. Build AI agents, automate workflows, and create dynamic content with ease.

</div>

---

## Why Notionary?

- **Smart Discovery**: Find pages and databases by name—no more hunting for URLs or IDs
- **Rich Markdown**: Convert extended Markdown (callouts, toggles, columns) directly into beautiful Notion blocks
- **Async-First**: Built for modern Python with full async/await support and high performance
- **AI-Ready**: Perfect foundation for AI agents that generate and manage Notion content
- **Round-Trip**: Read existing content, modify it, and write it back while preserving formatting

---

## Quick Start

```bash
pip install notionary
```

Set up your [Notion integration](https://www.notion.so/profile/integrations) and add your token:

```bash
NOTION_SECRET=your_integration_key
```

### Simple Flow: Find → Create → Update

<video width="100%" controls>
  <source src="./static/demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

_Demo: Converting markdown to structured Notion content with callouts, columns, and tables_

```python
import asyncio
from notionary import NotionPage, NotionDatabase

async def main():
    # Work with pages - find by name, no exact match needed!
    page = await NotionPage.from_page_name("Meeting Notes")

    # Direct Markdown - quick & intuitive
    await page.append_markdown("""
    ## Action Items
    - Review project proposal
    - Schedule team meeting
    - Update documentation

    [callout](Important meeting decisions require follow-up "💡")
    """)

    # Builder Pattern - type-safe & powerful for complex layouts
    await page.append_markdown(lambda builder: (
        builder
        .h2("Project Status")
        .callout("Project milestone reached!", "🎉")
        .columns(
            lambda col: (col
                .h3("Completed")
                .bulleted_list(["API design", "Database setup", "Authentication"])
            ),
            lambda col: (col
                .h3("In Progress")
                .bulleted_list(["Frontend UI", "Testing", "Documentation"])
            )
        )
        .table(
            headers=["Task", "Owner", "Due Date"],
            rows=[
                ["Launch prep", "Alice", "2024-03-15"],
                ["Marketing", "Bob", "2024-03-20"]
            ]
        )
    ))

asyncio.run(main())
```

### Create Rich Database Entries

<video width="100%" controls>
  <source src="./static/create_page_in_database_demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

_Demo: Creating a styled project page in a Notion database with properties, content, and rich formatting_

```python
# Work with databases - connect and create styled entries
db = await NotionDatabase.from_database_name("Projects")

# Create new project with full styling
project = await db.create_blank_page()
await project.set_title("New Marketing Campaign")
await project.set_emoji_icon("🚀")
await project.set_random_gradient_cover()

# Set database properties
await project.set_property_value_by_name("Status", "Planning")
await project.set_property_value_by_name("Priority", "High")
await project.set_property_value_by_name("Team Lead", "sarah@company.com")

# Add rich content to the new page
await project.replace_content(lambda builder: (
    builder
    .h1("Campaign Overview")
    .callout("New marketing initiative targeting Q2 growth", "🎯")
    .h2("Goals & Objectives")
    .numbered_list([
        "Increase brand awareness by 25%",
        "Generate 500 qualified leads",
        "Launch in 3 target markets"
    ])
    .h2("Budget Breakdown")
    .table(
        headers=["Category", "Allocated", "Spent", "Remaining"],
        rows=[
            ["Digital Ads", "$15,000", "$3,200", "$11,800"],
            ["Content Creation", "$8,000", "$1,500", "$6,500"],
            ["Events", "$12,000", "$0", "$12,000"]
        ]
    )
    .divider()
    .toggle("Technical Requirements", lambda toggle: (
        toggle
        .paragraph("Platform specifications and integration details.")
        .bulleted_list([
            "CRM integration with Salesforce",
            "Analytics tracking setup",
            "Landing page development"
        ])
    ))
))

print(f"✅ Created styled project: {project.url}")
```

### Extended Markdown Syntax

Notionary supports rich formatting with callouts, toggles, multi-column layouts, tables, media embeds, and more. Use either direct markdown syntax or the type-safe builder pattern.

See the complete [Block Types documentation](https://mathisarends.github.io/notionary/blocks/) for all available formatting options and syntax examples.

## What You Can Build

- **AI Content Generation** - Perfect for AI agents that create structured reports and documentation
- **Workflow Automation** - Update project status, sync data between databases, generate reports
- **Dynamic Documentation** - Auto-generate team docs, API references, and knowledge bases
- **Content Management** - Bulk page updates, template generation, and content migration

## Core Features

| Feature              | Description                                            |
| -------------------- | ------------------------------------------------------ |
| **Smart Discovery**  | Find pages/databases by name with fuzzy matching       |
| **Rich Markdown**    | Extended syntax for callouts, toggles, columns, tables |
| **Async-First**      | Modern Python with full async/await support            |
| **Round-Trip**       | Read content as markdown, edit, and write back         |
| **AI-Ready**         | Generate system prompts for AI content creation        |
| **All Block Types**  | Support for every Notion block type                    |
| **Type Safety**      | Full type hints for better IDE support                 |
| **High Performance** | Efficient batch operations and caching                 |

## Examples & Documentation

Explore comprehensive guides and real-world examples:

- **[📖 Full Documentation](https://mathisarends.github.io/notionary/)** - Complete API reference and guides
- **[Getting Started](https://mathisarends.github.io/notionary/get-started/)** - Quick setup and first steps
- **[Page Management](https://mathisarends.github.io/notionary/page/)** - Work with page content and properties
- **[Database Operations](https://mathisarends.github.io/notionary/database/)** - Query and manage databases
- **[Block Types](https://mathisarends.github.io/notionary/blocks/)** - Complete formatting reference

Check out the `examples/` directory for hands-on tutorials:

### Core Examples

- **[Page Management](examples/page_example.py)** - Create, update, and manage pages
- **[Database Operations](examples/database.py)** - Connect to and query databases
- **[Workspace Discovery](examples/workspace_discovery.py)** - Explore your workspace

### Markdown Examples

- **[Basic Formatting](examples/markdown/basic.py)** - Text, lists, and links
- **[Callouts](examples/markdown/callout.py)** - Eye-catching information boxes
- **[Toggles](examples/markdown/toggle.py)** - Collapsible content sections
- **[Multi-Column](examples/markdown/columns.py)** - Side-by-side layouts
- **[Tables](examples/markdown/table.py)** - Structured data presentation

## Contributing

We'd love your help making Notionary even better!

Whether it's fixing bugs, adding features, improving docs, or sharing examples - all contributions are welcome.

See our [Contributing Guide](https://mathisarends.github.io/notionary/contributing/) to get started.

---

<div align="center">

**Ready to transform your Notion workflow?**

[📖 Read the Docs](https://mathisarends.github.io/notionary/) • [Getting Started](https://mathisarends.github.io/notionary/get-started/) • [Examples](examples/)

Built with ❤️ for the Python community

</div>
