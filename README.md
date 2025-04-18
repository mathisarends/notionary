# Notionary 📝

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Notionary** is a powerful Python library for interacting with the Notion API, making it easy to create, update, and manage Notion pages and databases programmatically with a clean, intuitive interface. It's specifically designed to be the foundation for AI-driven Notion content generation.

## Features

- **Rich Markdown Support**: Create Notion pages using intuitive Markdown syntax with custom extensions
- **Extensible Block Registry**: Add, customize, or remove Notion block elements with a flexible registry pattern
- **LLM-Ready Prompts**: Generate system prompts explaining Markdown syntax for LLMs to create Notion content
- **Dynamic Database Operations**: Create, update, and query database entries with schema auto-detection
- **Async-First Design**: Built for modern Python with full async/await support
- **Schema-Based Validation**: Automatic property validation based on database schemas
- **Intelligent Content Conversion**: Bidirectional conversion between Markdown and Notion blocks

## Installation

```bash
pip install notionary
```

## Block Registry & Builder

Notionary uses a flexible registry pattern with a builder to customize which Notion elements are supported:

```python
from notionary.elements.block_element_registry_builder import BlockElementRegistryBuilder

# Create a registry with standard Notion elements
registry = BlockElementRegistryBuilder.create_standard_registry()

# Or build a custom registry with only the elements you need
custom_registry = (
    BlockElementRegistryBuilder()
    .with_headings()
    .with_callouts()
    .with_toggles()
    .with_lists()
    .with_tables()
    .with_paragraphs()
    .build()
)

# Generate an LLM system prompt explaining the Markdown syntax
llm_system_prompt = registry.generate_llm_prompt()
```

## Custom Markdown Syntax

Notionary extends standard Markdown with special syntax to support Notion-specific features:

### Text Formatting

- Standard Markdown: `**bold**`, `*italic*`, `~~strikethrough~~`, `` `code` ``
- Highlights: `==highlighted text==`, `==red:warning==`, `==blue:note==`

### Block Elements

#### Callouts

```markdown
!> [💡] This is a default callout with the light bulb emoji  
!> [🔔] This is a callout with a bell emoji  
!> {blue_background} [💧] This is a blue callout with a water drop emoji  
!> {yellow_background} [⚠️] Warning: This is an important note
```

#### Toggles

```markdown
+++ How to use NotionPageManager

1. Initialize with NotionPageManager
2. Update metadata with set_title(), set_page_icon(), etc.
3. Add content with replace_content() or append_markdown()
```

#### Bookmarks

```markdown
[bookmark](https://notion.so "Notion Homepage" "Your connected workspace")
```

#### Multi-Column Layouts

```markdown
::: columns
::: column
Content for first column
:::
::: column
Content for second column
:::
:::
```

And more:

- Tables with standard Markdown syntax
- Code blocks with syntax highlighting
- To-do lists with `- [ ]` and `- [x]`
- Block quotes with `>`

## AI-Ready LLM Prompt Generation

Notionary can automatically generate comprehensive system prompts for LLMs to understand Notion's custom Markdown syntax:

```python
from notionary.elements.block_element_registry_builder import BlockElementRegistryBuilder

registry = BlockElementRegistryBuilder.create_standard_registry()
llm_system_prompt = registry.generate_llm_prompt()

# Use this prompt with your LLM to generate Notion-compatible Markdown
print(llm_system_prompt)
```

This makes Notionary the perfect foundation for AI-driven Notion content generation, enabling LLMs to create properly formatted Notion pages.

## Database Management

Notionary makes it easy to work with Notion databases, automatically handling schema detection and property conversion:

```python
import asyncio
from notionary import NotionDatabaseFactory

async def main():
    # Find database by name with fuzzy matching
    db_manager = await NotionDatabaseFactory.from_database_name("Projects")

    # Create a new page with properties
    properties = {
        "Title": "Created via Notionary",
        "Status": "In Progress",
        "Priority": "High"
    }

    page = await db_manager.create_blank_page()

    # Set page content with rich Markdown
    await page.set_title("My New Project")
    await page.set_page_icon(emoji="🚀")

    markdown = """
    # Project Overview

    !> [💡] This page was created programmatically using Notionary.

    ## Tasks
    - [ ] Define project scope
    - [ ] Create timeline
    - [ ] Assign resources

    +++ Implementation Details
      This project will use our standard architecture with custom extensions.
    """

    await page.replace_content(markdown)

if __name__ == "__main__":
    asyncio.run(main())
```

## Page Content Management

Create rich Notion pages using enhanced Markdown:

```python
from notionary import NotionPage

async def create_rich_page():
    url = "https://www.notion.so/Your-Page-1cd389d57bd381e58be9d35ce24adf3d"
    page_manager = NotionPage(url=url)

    await page_manager.set_title("Notionary Demo")
    await page_manager.set_page_icon(emoji="✨")
    await page_manager.set_page_cover("https://images.unsplash.com/photo-1555066931-4365d14bab8c")

    markdown = '''
    # Notionary Rich Content Demo

    !> [💡] This page was created with Notionary's custom Markdown syntax.

    ## Features
    - Easy-to-use Python API
    - **Rich** Markdown support
    - Async functionality

    +++ Implementation Details
      Notionary uses a custom converter to transform Markdown into Notion blocks.
      This makes it easy to create rich content programmatically.
    '''

    await page_manager.replace_content(markdown)
```

## Examples

See the [examples folder](examples/) for more comprehensive demonstrations:

- [Database discovery and querying](examples/database_discovery_example.py)
- [Rich page creation with Markdown](examples/page_example.py)
- [Database factory usage](examples/database_factory_example.py)
- [Page lookup and access](examples/page_factory_by_url_example.py)
- [Iterating through database entries](examples/iter_database_example.py)

## Perfect for AI Agents and Automation

- **LLM Integration**: Generate Notion-compatible content with LLMs using the system prompt generator
- **Dynamic Content Generation**: AI agents can generate content in Markdown and render it as Notion pages
- **Schema-Aware Operations**: Automatically validate and format properties
- **Simplified API**: Easier integration with AI workflows

## License

MIT

## Contributing

Contributions welcome — feel free to submit a pull request!
