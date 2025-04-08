# Notionary 📝

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Notionary** is a powerful Python library for interacting with the Notion API, making it easy to create, update, and manage Notion pages and databases programmatically with a clean, intuitive interface.

## Features

- **Rich Markdown Support**: Write Notion pages using intuitive Markdown syntax with custom extensions
- **Dynamic Database Operations**: Create, update, and query database entries with schema auto-detection
- **Async-First Design**: Built for modern Python with full async/await support
- **Schema-Based Validation**: Automatic property validation based on database schemas
- **Intelligent Content Conversion**: Bidirectional conversion between Markdown and Notion blocks

## Installation

```bash
pip install notionary
```

## Custom Markdown Syntax

Notionary extends standard Markdown with special syntax to support Notion-specific features:

### Text Formatting

- Standard Markdown: `**bold**`, `*italic*`, `~~strikethrough~~`, `` `code` ``
- Highlights: `==highlighted text==`, `==red warning==`, `==blue==`

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

## Database Management

Notionary makes it easy to work with Notion databases, automatically handling schema detection and property conversion:

```python
import asyncio
from notionary.core.database.notion_database_manager import NotionDatabaseManager

async def main():
    database_id = "1a6389d5-7bd3-8097-aa38-e93cb052615a"
    db = NotionDatabaseManager(database_id)
    await db.initialize()

    properties = {
        "Title": "Created via Notionary",
        "Description": "This entry was created using Notionary.",
        "Status": "In Progress",
        "Priority": "High"
    }

    result = await db.create_page(properties)

    if result["success"]:
        page_id = result["page_id"]
        await db.update_page(page_id, {"Status": "Completed"})

    filter_conditions = {
        "property": "Status",
        "status": {"equals": "Completed"}
    }

    pages = await db.get_pages(limit=10, filter_conditions=filter_conditions)

    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Finding Databases by Name

Use fuzzy matching to find databases:

```python
from notionary.core.database.notion_database_manager_factory import NotionDatabaseFactory

async def main():
    db_manager = await NotionDatabaseFactory.from_database_name("Projects")
    print(f"Found database: {db_manager.title}")
    await db_manager.close()
```

## Page Content Management

Create rich Notion pages using enhanced Markdown:

```python
from notionary.core.page.notion_page_manager import NotionPageManager

async def create_rich_page():
    url = "https://www.notion.so/Your-Page-1cd389d57bd381e58be9d35ce24adf3d"
    page_manager = NotionPageManager(url=url)

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

## Perfect for AI Agents and Automation

- **Dynamic Content Generation**: AI agents can generate content in Markdown and render it as Notion pages
- **Schema-Aware Operations**: Automatically validate and format properties
- **Simplified API**: Easier integration with AI workflows

## Examples

See the `examples` folder for:

- Database discovery and querying
- Rich page creation with Markdown
- Entry management
- Metadata manipulation

## License

MIT

## Contributing

Contributions welcome — feel free to submit a pull request!
