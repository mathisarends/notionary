# Welcome to Notionary

Transform complex Notion API interactions into simple, Pythonic code. Whether you're building AI agents, automating workflows, or creating dynamic content, Notionary makes it effortless.

## Quick Start

Ready to get started? Head over to our [Getting Started Guide](get-started/index.md) to begin your journey with Notionary.

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

## Key Features

- **Object-Oriented Design** - Clean, intuitive classes for Pages, Databases, and Workspaces
- **Rich Markdown Support** - Transform extended Markdown (callouts, toggles, columns) into Notion blocks
- **Smart Discovery** - Find pages and databases by name with fuzzy matching
- **Async-First Architecture** - Built for modern Python with full async/await support
- **AI-Ready Integration** - Generate LLM system prompts for AI content creation

## What's Next?

1. 📚 **[Get Started](get-started/index.md)** - Learn the basics and set up your first project
2. 🗄️ **[Database Operations](database/index.md)** - Work with Notion databases
3. 📄 **[Page Management](page/index.md)** - Create and manage pages
4. 🧱 **[Blocks & Formatting](blocks/index.md)** - Rich content creation

<div align="center">
  <p>Build something amazing with Notionary! 🚀</p>
</div>
