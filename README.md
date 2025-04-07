# Notionary 📝

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Notionary** is a powerful Python library for interacting with the Notion API, making it easy to create, update, and manage Notion pages and databases programmatically with a clean, intuitive interface.

## 🌟 Features

- **High-level APIs** for database and page management
- **Custom Markdown support** with rich Notion-specific extensions
- **Async-first design** for optimal performance
- **Intelligent conversion** between Markdown and Notion blocks
- **Comprehensive block support** including:
  - Rich text formatting
  - Code blocks with syntax highlighting
  - Tables
  - Callouts with custom colors
  - Toggle lists
  - Bookmarks
  - Images and videos
  - Lists (bulleted, numbered, to-do)
  - And more!

## 📋 Installation

```bash
pip install notionary
```

## 🔑 Authentication

Notionary uses your Notion integration token for authentication:

```python
# Set your token as an environment variable
export NOTION_SECRET=your_integration_token

# Or provide it directly when initializing clients
client = NotionClient(token="your_integration_token")
```

Make sure your integration has been added to the pages or databases you want to access.

## 📚 Usage

### 🏢 Working with Databases

```python
import asyncio
from notionary.core.database.notion_database_manager import NotionDatabaseManager

async def main():
    # Initialize with your database ID
    database_id = "1a6389d5-7bd3-8097-aa38-e93cb052615a"
    db = NotionDatabaseManager(database_id)

    # Load database schema
    await db.initialize()

    # Get database name
    db_name = await db.get_database_name()
    print(f"Working with database: {db_name}")

    # Get property types
    property_types = await db.get_property_types()

    # Create a new page
    properties = {
        "Title": "Created with Notionary",
        "Tags": ["python", "notion"],
        "Status": "In Progress",
        "Priority": "High"
    }

    result = await db.create_page(properties)
    if result["success"]:
        print(f"Page created with ID: {result['page_id']}")

    # Get pages from the database
    pages = await db.get_pages(limit=5)
    for page in pages:
        print(f"- {page.title}")

    # Close the connection
    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### 📄 Working with Pages

````python
import asyncio
from notionary.core.page.notion_page_manager import NotionPageManager

async def main():
    page = NotionPageManager(url="https://www.notion.so/myworkspace/Page-Title-1cd389d57bd3...")

    # Set page metadata
    await page.set_title("Updated Page Title")
    await page.set_page_icon(emoji="✨")
    await page.set_page_cover("https://images.unsplash.com/photo-1.jpg")

    # Add content using rich Markdown
    markdown = """
    # Welcome to Notionary

    !> [💡] **Tip:** This callout uses custom Notion-flavored Markdown

    ## Features
    - Easy-to-use Python API
    - Rich Markdown support
    - **Bold text** and *italic text*
    - ==yellow:Highlighted text== with colors

    | Feature | Status |
    | ------- | ------ |
    | Markdown | ✅ |
    | Tables | ✅ |
    | Callouts | ✅ |

    +++ Click to expand
      This content is hidden in a toggle block!

    ```python
    # You can include code blocks too
    print("Hello from Notionary!")
    ```
    """

    await page.replace_content(markdown)

if __name__ == "__main__":
    asyncio.run(main())
````

### 🔍 Exploring Databases

```python
import asyncio
from notionary.core.database.notion_database_schema import NotionDatabaseAccessor

async def main():
    accessor = NotionDatabaseAccessor()

    # Discover all databases in your workspace
    async for database in accessor.iter_databases():
        db_id = database.get("id", "Unknown ID")
        title = accessor.extract_database_title(database)

        print(f"\nDatabase: {title}")
        print(f"ID: {db_id}")

        # Show properties
        if "properties" in database:
            print("\nProperties:")
            for prop_name, prop_details in database["properties"].items():
                prop_type = prop_details.get("type", "unknown")
                print(f"  • {prop_name} ({prop_type})")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📝 Custom Notion Markdown Syntax

Notionary supports a rich set of Markdown extensions to utilize Notion's features:

### Text Formatting

- **Bold text** = `**Bold text**`
- _Italic text_ = `*Italic text*`
- ~~Strikethrough~~ = `~~Strikethrough~~`
- `Code` = `` `Code` ``

### Highlights

- ==This is highlighted in yellow== = `==This is highlighted in yellow==`
- ==red:Important warning== = `==red:Important warning==`
- ==blue:Note== = `==blue:Note==`

### Callouts

```
!> [💡] This is a default callout

!> {blue_background} [💧] This is a blue callout
```

### Toggles

```
+++ Click to expand
  This is hidden content
  You can put any content here
```

### Code Blocks

````
```python
print("Hello, World!")
````

```

### Tables
```

| Header 1 | Header 2 |
| -------- | -------- |
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

```

## 🌐 Examples

See the `examples/` directory for more detailed examples:

- `example_notion_database_accessor.py` - Discover databases in your workspace
- `example_notion_database_manager.py` - Create and manage database entries
- `example_page_manager.py` - Create rich Notion pages with custom content
- `iter_database_entries.py` - Efficiently iterate through database entries

## 📖 Documentation

For more detailed documentation:

1. [Getting Started Guide](docs/getting-started.md)
2. [API Reference](docs/api-reference.md)
3. [Markdown Syntax](docs/markdown-syntax.md)

## 🧰 Requirements

- Python 3.8+
- `httpx`
- `python-dotenv`
- `typing-extensions`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ - Happy automating with Notion!
```
