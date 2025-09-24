# NotionPage

The `NotionPage` class provides comprehensive functionality for working with Notion pages. Pages are one of Notion's core building blocks, serving as the fundamental content containers that can exist independently or as entries within databases.

## Overview

Notion pages are versatile content containers that support rich text, media, and structured blocks. They can function as standalone documents or as structured entries within databases with custom properties and metadata.

For complete information about Notion pages and their capabilities, see the [official Notion API Page reference](https://developers.notion.com/reference/page).

## Page Connection

Connect to existing pages using multiple methods:

```python
from notionary import NotionPage

# Find by name with fuzzy matching
page = await NotionPage.from_title("Meeting Notes")

# Connect by ID
page = await NotionPage.from_page_id("12345678-1234-1234-1234-123456789012")

# Load from URL
page = await NotionPage.from_url("https://notion.so/workspace/page-id")
```

### Page Information

Access page metadata and properties:

```python
# Basic information
print(f"Page: {page.title}")
print(f"ID: {page.id}")
print(f"URL: {page.url}")
print(f"Emoji: {page.emoji_icon}")

# Status information
print(f"Archived: {page.is_archived}")
print(f"In Trash: {page.is_in_trash}")
```

## Content Management

Read and write page content using markdown:

```python
# Read content
content = await page.get_text_content()

# Add content
await page.append_markdown("## New Section\nAdditional content here.")

# Replace all content
await page.replace_content("# Fresh Start\nCompletely new content.")

# Clear content
await page.clear_page_content()
```

## Page Customization

Customize page appearance and metadata:

```python
# Update title and appearance
await page.set_title("Updated Page Title")
await page.set_emoji_icon("📚")
await page.set_cover("https://example.com/banner.jpg")

# Archive page
await page.archive()
```

## Content Features

Create complex layouts with extended markdown syntax:

```python
# Builder pattern for structured content
await page.append_markdown(lambda builder: (
    builder
    .h1("Project Overview")
    .callout("Important information", "💡")
    .columns(
        lambda col: col.h3("Left").bulleted_list(["Item 1", "Item 2"]),
        lambda col: col.h3("Right").bulleted_list(["Item A", "Item B"])
    )
))
```

### Block Registry

Customize supported markdown elements:

```python
# Access block registry builder
registry_builder = page.block_registry_builder

# Customize supported blocks for specific pages
custom_registry = (registry_builder
    .with_headings()
    .with_callouts()
    .with_tables()
    .build())
```

## Database Integration

For pages within databases, manage custom properties:

```python
# Read database properties
status = await page.get_property_value_by_name("Status")
priority = await page.get_property_value_by_name("Priority")

# Write database properties
await page.set_property_value_by_name("Status", "In Progress")
await page.set_property_value_by_name("Due Date", "2024-03-15")

# Work with relations
await page.set_relation_property_values_by_name("Related", ["Page A", "Page B"])

# Get available options
options = await page.get_options_for_property_by_name("Status")
```

## Supported Content Types

Notionary supports all Notion block types including:

- **Text Blocks** - Paragraphs, headings, quotes, callouts
- **Lists** - Bulleted, numbered, and to-do lists
- **Rich Media** - Images, videos, files, embeds
- **Layout** - Columns, dividers, tables
- **Interactive** - Toggles, toggleable headings
- **Mathematical** - LaTeX equations
- **Navigation** - Table of contents, breadcrumbs
- **Code** - Syntax-highlighted code blocks

## Next Steps

- Learn how to [connect to pages](connecting.md) in your workspace
- Explore [content management](content.md) for rich markdown operations
- Review [block types](../blocks/index.md) for formatting options
