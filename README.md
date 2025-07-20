<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./static/notionary-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="./static/notionary-light.png">
  <img alt="Notionary logo: dark mode shows a white logo, light mode shows a black logo." src="./static/browser-use.png"  width="full">
</picture>

<h1 align="center">Notion API simplified for Python developers 🐍</h1>

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

- **Object-Oriented Design**: Clean, intuitive classes for Pages, Databases, and Workspaces with full CRUD operations
- **Rich Markdown to Notion**: Convert extended Markdown (callouts, toggles, columns) directly into beautiful Notion blocks
- **Smart Discovery**: Find pages and databases by name with fuzzy matching - no more hunting for URLs
- **Async-First Architecture**: Built for modern Python with full async/await support and high performance
- **AI-Ready Integration**: Generate LLM system prompts and let AI agents create Notion content seamlessly

---

# Quick start
```bash
pip install notionary
```

- Set up your Notion integration (notion.so/profile/integrations)
- Add your integration key in your `.env` file.

```bash
NOTION_SECRET=YOUR_INTEGRATION_KEY
```

### Creating and Managing Pages 🚀
```python
from notionary import NotionPage

async def main():
    # Simpy find an existing page by its title
    page = await NotionPage.from_page_name("My Test Page")
    
    # Add rich content with custom Markdown
    content = """
    # 🚀 Generated with Notionary
    
    !> [💡] This page was created programmatically!
    
    ## Features
    - **Rich** Markdown support
    - Database integration
    - AI-ready content generation
    
    +++ Click to see more details
    | Notionary makes it easy to create beautiful Notion pages
    | directly from Python code with intuitive Markdown syntax.
    """
    
    await page.replace_content(content)
    print(f"✅ Page updated: {page.url}")

asyncio.run(main())
```

---

### Working with Databases 🔥

```python
import asyncio
from notionary import NotionDatabase

async def main():
  # Connect to database by name (fuzzy matching)
  db = await NotionDatabase.from_database_name("Projects")

  # Create a new page with properties
  page = await db.create_blank_page()
  await page.set_title("🆕 New Project Entry")
  await page.set_property_value_by_name("Status", "In Progress")
  await page.set_property_value_by_name("Priority", "High")
  
  # find pages created in the last 7 days
  count = 0
  async for page in db.iter_pages_with_filter(
      db.create_filter().with_created_last_n_days(7)
  ):
      count += 1
      print(f"{count:2d}. {page.emoji_icon or '📄'} {page.title}")

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

### Multi-Column Layout

```markdown
::: columns
::: column

## Left Column

- Item 1
- Item 2
- Item 3
  :::
  ::: column

## Right Column

This text appears in the second column. Multi-column layouts are perfect for:

- Comparing features
- Creating side-by-side content
- Improving readability of wide content
  :::
  :::
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

## Examples

Explore the `examples/` directory for comprehensive guides:

### 🚀 Core Examples
- [**Page Management**](examples/page_example.py) - Create, update, and manage Notion pages
- [**Page Operations**](examples/page.py) - Advanced page manipulation and content handling
- [**Database Operations**](examples/database.py) - Connect to and manage Notion databases
- [**Database Iteration**](examples/database_iteration.py) - Query and filter database entries
- [**Workspace Discovery**](examples/workspace_discovery.py) - Explore and discover your Notion workspace

### 📝 Markdown Examples
- [**Basic Formatting**](examples/markdown/basic.py) - Text formatting, lists, and basic elements
- [**Callouts**](examples/markdown/callout.py) - Create beautiful callout blocks with icons
- [**Toggles**](examples/markdown/toggle.py) - Collapsible content sections
- [**Multi-Column Layouts**](examples/markdown/columns.py) - Side-by-side content arrangement
- [**Code Blocks**](examples/markdown/code.py) - Syntax-highlighted code examples
- [**Tables**](examples/markdown/table.py) - Structured data presentation
- [**Media Embeds**](examples/markdown/embed.py) - Images, videos, and rich media
- [**Audio Content**](examples/markdown/audio.py) - Audio file integration

Each example is self-contained and demonstrates specific features with practical use cases.

## Contributing

Contributions welcome — feel free to submit a pull request!
