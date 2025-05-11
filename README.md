# Notionary 📝

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Notionary** is a powerful Python library for interacting with the Notion API, making it easy to create, update, and manage Notion pages and databases programmatically with a clean, intuitive interface. It's specifically designed to be the foundation for AI-driven Notion content generation.

---

## Features

- **Rich Markdown Support**: Create Notion pages using intuitive Markdown syntax with custom extensions
- **Dynamic Database Operations**: Create, update, and query database entries with schema auto-detection
- **Extensible Block Registry**: Add, customize, or remove Notion block elements with a flexible registry pattern
- **LLM-Ready Prompts**: Generate system prompts explaining Markdown syntax for LLMs to create Notion content
- **Async-First Design**: Built for modern Python with full async/await support
- **Schema-Based Validation**: Automatic property validation based on database schemas
- **Intelligent Content Conversion**: Bidirectional conversion between Markdown and Notion blocks

---

## Installation

```bash
pip install notionary
```

---

## Quick Start

### Creating and Managing Pages

```python
import asyncio
from notionary import NotionPage

async def main():
    # Create a page from URL
    page = NotionPage.from_url("https://www.notion.so/your-page-url")

    # Or find by name
    page = await NotionPage.from_page_name("My Project Page")

    # Update page metadata
    await page.set_title("Updated Title")
    await page.set_emoji_icon("🚀")
    await page.set_random_gradient_cover()

    # Add markdown content
    markdown = """
    # Project Overview

    !> [💡] This page was created programmatically using Notionary.

    ## Features
    - **Rich** Markdown support
    - Async functionality
    - Custom syntax extensions

    +++ Implementation Details
    | Notionary uses a custom converter to transform Markdown into Notion blocks.
    | This makes it easy to create rich content programmatically.
    """

    await page.replace_content(markdown)

if __name__ == "__main__":
    asyncio.run(main())
```

### Working with Databases

```python
import asyncio
from notionary import NotionDatabase, DatabaseDiscovery

async def main():
    # Discover available databases
    discovery = DatabaseDiscovery()
    await discovery()

    # Connect to a database by name
    db = await NotionDatabase.from_database_name("Projects")

    # Create a new page in the database
    page = await db.create_blank_page()

    # Set properties
    await page.set_property_value_by_name("Status", "In Progress")
    await page.set_property_value_by_name("Priority", "High")

    # Query pages from database
    async for page in db.iter_pages():
        title = await page.get_title()
        print(f"Page: {title}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Custom Markdown Syntax

Notionary extends standard Markdown with special syntax to support Notion-specific features:

### Text Formatting

- Standard: `**bold**`, `*italic*`, `~~strikethrough~~`, `` `code` ``
- Links: `[text](url)`
- Quotes: `> This is a quote`
- Divider: `---`

### Callouts

```markdown
!> [💡] This is a default callout with the light bulb emoji  
!> [🔔] This is a notification with a bell emoji  
!> [⚠️] Warning: This is an important note
```

### Toggles

```markdown
+++ How to use Notionary
| 1. Initialize with NotionPage  
| 2. Update metadata with set_title(), set_emoji_icon(), etc.  
| 3. Add content with replace_content() or append_markdown()
```

### Code Blocks

```python
def hello_world():
    print("Hello from Notionary!")
```

### To-do Lists

```markdown
- [ ] Define project scope
- [x] Create timeline
- [ ] Assign resources
```

### Tables

```markdown
| Feature         | Status      | Priority |
| --------------- | ----------- | -------- |
| API Integration | Complete    | High     |
| Documentation   | In Progress | Medium   |
```

### More Elements

```markdown
![Caption](https://example.com/image.jpg)  
@[Caption](https://youtube.com/watch?v=...)  
[bookmark](https://example.com "Title" "Description")
```

## Block Registry & Customization

```python
from notionary import NotionPage, BlockRegistryBuilder

# Create a custom registry with only the elements you need
custom_registry = (
    BlockRegistryBuilder()
    .with_headings()
    .with_callouts()
    .with_toggles()
    .with_code()
    .with_todos()
    .with_paragraphs()
    .build()
)

# Apply this registry to a page
page = NotionPage.from_url("https://www.notion.so/your-page-url")
page.block_registry = custom_registry
ark
# Replace content using only supported elements
await page.replace_content("# Custom heading with selected elements only")
```

## AI-Ready: Generate LLM Prompts

```python
from notionary import BlockRegistryBuilder

# Create a registry with all standard elements
registry = BlockRegistryBuilder.create_full_registry()

# Generate the LLM system prompt
llm_system_prompt = registry.get_notion_markdown_syntax_prompt()
print(llm_system_prompt)
```

## Examples

See the `examples/` folder for:

- [Database discovery and querying](examples/database_discovery_example.py)
- [Rich page creation with Markdown](examples/page_example.py)
- [Database management](examples/database_management_example.py)
- [Iterating through database entries](examples/database_iteration_example.py)
- [Temporary usage & debugging](examples/temp.py)

## Perfect for AI Agents and Automation

- **LLM Integration**: Generate Notion-compatible content with any LLM using the system prompt generator
- **Dynamic Content Generation**: AI agents can generate content in Markdown and render it directly as Notion pages
- **Schema-Aware Operations**: Automatically validate and format properties based on database schemas
- **Simplified API**: Clean, intuitive interface for both human developers and AI systems

## Contributing

Contributions welcome — feel free to submit a pull request!
