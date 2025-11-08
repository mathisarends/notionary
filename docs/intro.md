# Notionary

Transform complex Notion API interactions into simple, Pythonic code. Whether you're building AI agents, automating workflows, or creating dynamic content, Notionary makes it effortless.

## Why use Notionary?

- **Object-Oriented Wrapper** – Instead of handling deeply nested JSON and dictionaries, Notionary offers clean Python classes for working with entities such as Datasources, Pages, and Databases. This makes it easy and intuitive to interact with your Notion content.
- **Direct Access to Objects** – Methods and attributes are available out-of-the-box, so you can work with your data without manual parsing or mapping.
- **Less Boilerplate, More Productivity** – Write less code and focus on your application logic.
- **Markdown & Block Support** – Extended Markdown is automatically converted to Notion blocks.
- **Async-First Architecture** – Modern Python with full async/await support for fast and scalable workflows.

### Installation

```bash
pip install notionary
```

### Hello World Example

```python
# Find a page and update it with rich content
page = await NotionPage.from_title("My Project")
await page.replace_content("""
# 🚀 Project Overview

!> [💡] This page was created programmatically!

+++ Implementation Details
| Built with Notionary's intuitive Python API
| Rich Markdown support with custom extensions
""")
```

(_If running this_, ensure you set the NOTION_SECRET environment variable)

```bash
export NOTION_SECRET=ntn_...
```
