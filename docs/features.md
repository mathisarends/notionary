# Features

Notionary provides a comprehensive set of features for automating your Notion workspace with Python.

## Database Operations

Connect to databases using fuzzy name matching - no need for complex URLs or IDs.

```python
# Find database by name (fuzzy matching works!)
db = await NotionDatabase.from_database_name("My Projects")
print(f"Connected to: {db.title}")
```

### Page Creation & Management

Create pages in databases and set properties programmatically.

```python
# Create a new page in the database
page = await db.create_blank_page()
await page.set_title("🆕 New Project Entry")

# Set database properties
await page.set_property_value_by_name("Status", "In Progress")
await page.set_property_value_by_name("Priority", "High")
```

### Advanced Filtering & Querying

Query database pages with powerful filters and iterate through results.

```python
# Query recent pages with filters
async for i, page in enumerate(db.iter_pages_with_filter(
    db.create_filter().with_created_last_n_days(7)
), start=1):
    print(f"{i}. {page.emoji_icon or '📄'} {page.title}")
```

## Page Management

Find pages by name without needing exact matches or URLs.

```python
# Find page by name (fuzzy matching supported)
page = await NotionPage.from_page_name("Meeting Notes")
```

### Page Metadata Control

Full control over page appearance and metadata.

```python
# Update page metadata
await page.set_title("🚀 Updated Project Title")
await page.set_emoji_icon("🚀")
await page.set_random_gradient_cover()
```

### Content Management

Add, replace, or append content using rich Markdown syntax.

```python
# Replace entire page content
await page.replace_content(markdown_content)

# Append new content with optional divider
await page.append_markdown(markdown_content, append_divider=True)

# Get existing content as markdown
text_content = await page.get_text_content()
```

## Workspace Discovery

Discover all databases in your Notion workspace.

```python
workspace = NotionWorkspace()

# List all databases
databases = await workspace.list_all_databases()
for db in databases:
    print(f"🗃️ {db.title} - {db.url}")
```

### Page Search

Search for pages across your entire workspace.

```python
# Search for specific pages
pages = await workspace.search_pages("meeting notes", limit=5)
for page in pages:
    print(f"📄 {page.title} - {page.url}")
```

## Rich Markdown Extensions

Notionary extends standard Markdown with Notion-specific elements.

### Basic Formatting

Standard Markdown with full support for text formatting, lists, and links.

```markdown
**Bold text**, _italic text_, `inline code`

- Bulleted lists

1. Numbered lists
2. For ordered content

[Links](https://example.com) and inline `code variables`
```

### Callouts

Create eye-catching callouts with custom emojis.

```markdown
!> [💡] This is a tip callout with a light bulb emoji
!> [⚠️] Warning: Important information here
!> [✅] Success: Operation completed successfully
```

### Toggles

Create collapsible content sections.

```markdown
+++ Click to expand details
++ Click to expand details
| Hidden content goes here
| Use pipe syntax for toggle content
| Perfect for hiding implementation details
```

### Multi-Column Layouts

Create side-by-side content with column layouts.

```markdown
::: columns
::: column

## Left Column

Content for the left side
:::
::: column

## Right Column

Content for the right side
:::
:::
```

### Code Blocks with Captions

Syntax-highlighted code blocks with optional captions.

````markdown
```python
def hello_world():
    print("Hello from Notionary!")
```
````

Caption: Basic Python function example

````

### Tables
Standard Markdown tables with full formatting support.

```markdown
| Feature | Status | Priority |
|---------|--------|----------|
| API Integration | Complete | High |
| Documentation | In Progress | Medium |
````

### Media Embeds

Embed videos, images, and other media content.

```markdown
# YouTube videos

<embed:Python Tutorial>(https://youtube.com/watch?v=...)

# Audio files

$[Podcast Episode](https://example.com/audio.mp3)

# Images with captions

![Image Caption](https://example.com/image.jpg)
```

## Async-First Architecture

Built from the ground up with async/await for high performance.

```python
import asyncio

async def main():
    # All operations are async
    page = await NotionPage.from_page_name("My Page")
    await page.replace_content("# Hello World")

    # Efficient batch operations
    async for page in db.iter_pages():
        await page.set_property_value_by_name("Status", "Updated")

asyncio.run(main())
```

### Error Handling & Retries

Robust error handling with automatic retries for network issues.

```python
try:
    page = await NotionPage.from_page_name("Non-existent Page")
except Exception as e:
    print(f"Page not found: {e}")
```

## AI-Ready Integration

Generate system prompts for AI agents to create Notion content.

```python
from notionary import BlockRegistryBuilder

# Create a registry with all elements
registry = BlockRegistryBuilder.create_registry()

# Generate LLM system prompt
llm_prompt = registry.get_notion_markdown_syntax_prompt()
print(llm_prompt)  # Use this to teach AI agents about Notionary's syntax
```

### AI Content Creation

Perfect foundation for AI agents that generate Notion content.

```python
# AI agents can use Notionary's extended Markdown
ai_generated_content = """
# AI-Generated Report

!> [🤖] This content was generated by an AI agent using Notionary!

++ Technical Details
+++ Technical Details
| The AI used natural language processing to analyze data
| and automatically generate this structured report.
"""

await page.replace_content(ai_generated_content)
```

## Extensible Design

### Custom Block Registry

Customize which Markdown elements are supported.

```python
from notionary import BlockRegistryBuilder

# Create custom registry with only needed elements
custom_registry = (
    BlockRegistryBuilder()
    .with_headings()
    .with_callouts()
    .with_toggles()
    .with_columns()
    .build()
)

# Apply to a page
page.block_registry = custom_registry
```

### Type Safety

Full type hints for better IDE support and code reliability.

```python
from notionary import NotionPage, NotionDatabase

# IDE will provide full autocompletion and type checking
page: NotionPage = await NotionPage.from_page_name("My Page")
db: NotionDatabase = await NotionDatabase.from_database_name("Projects")
```
