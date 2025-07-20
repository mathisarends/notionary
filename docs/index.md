# Notionary

The Notion API is powerful but rather hard to use, especially for complex tasks. For quick and dirty automation, the code gets messy real fast. Notionary fixes this.

Transform complex Notion API interactions into simple, Pythonic code. Whether you're building AI agents, automating workflows, or creating dynamic content, Notionary makes it effortless.

```python
# Find a page and update it with rich content
page = await NotionPage.from_page_name("My Project")
await page.replace_content("""
# 🚀 Project Overview

!> [💡] This page was created programmatically!

+++ Implementation Details
| Built with Notionary's intuitive Python API
| Rich Markdown support with custom extensions
""")
```

## Key Features

- **Object-Oriented Design** - Clean, intuitive classes for Pages, Databases, and Workspaces
- **Rich Markdown Support** - Transform extended Markdown (callouts, toggles, columns) into Notion blocks
- **Smart Discovery** - Find pages and databases by name with fuzzy matching
- **Async-First Architecture** - Built for modern Python with full async/await support
- **AI-Ready Integration** - Generate LLM system prompts for AI content creation

<div align="center">
  <p>Build something amazing with Notionary! 🚀</p>
</div>
