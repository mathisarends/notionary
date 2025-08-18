# Blocks

Notionary provides comprehensive support for all Notion block types through two powerful approaches. Each block type can be created, modified, and converted between Markdown and Notion format seamlessly.

> **Note:** The block APIs documented in this section are used within the `append_markdown()` and `replace_content()` methods of `NotionPage`. These methods accept either markdown strings or MarkdownBuilder functions to create rich content.

## Two Ways to Create Content

### 1. Direct Markdown Syntax

Use Notionary's extended Markdown syntax directly:

```python
# Simple markdown string
await page.append_markdown("""
# Welcome to Notionary

[callout](This is important information "💡")

## Features
- Easy to use
- Powerful API
- Great documentation
""")
```

### 2. Builder API Pattern

Use the MarkdownBuilder for programmatic content creation:

```python
# Builder pattern with callback
await page.append_markdown(lambda builder: (
    builder
    .heading("Welcome to Notionary", level=1)
    .callout("This is important information", emoji="💡")
    .heading("Features", level=2)
    .bulleted_list([
        "Easy to use",
        "Powerful API",
        "Great documentation"
    ])
))
```

Both approaches produce identical results, choose what fits your workflow best.

## Advanced Layout Examples

For more complex structured content like multi-column layouts, you can use both approaches:

**Direct Markdown Syntax:**

```python
await page.append_markdown("""
::: columns
::: column
## Getting Started
Follow these steps to begin:
1. Install the package
2. Set up authentication
3. Create your first page
:::

::: column
## Quick Tips
[callout](Pro tip: Use environment variables for API keys "💡")

- Start with simple examples
- Check the documentation
:::
:::
""")
```

**Builder API Pattern:**

```python
await page.append_markdown(lambda builder: (
    builder.heading("Documentation Overview", level=1)
    .columns(
        # Left column - main content
        lambda col: (
            col.heading("Getting Started", level=2)
            .paragraph("Follow these steps to begin:")
            .numbered_list([
                "Install the package",
                "Set up authentication",
                "Create your first page"
            ])
        ),
        # Right column - sidebar
        lambda col: (
            col.heading("Quick Tips", level=2)
            .callout("Pro tip: Use environment variables for API keys", "💡")
            .bulleted_list([
                "Start with simple examples",
                "Check the documentation"
            ])
        ),
        width_ratios=[0.6, 0.4]  # 60% left, 40% right
    )
))
```

## Complete Block Support

Notionary supports **all official Notion block types** as documented in the [Notion API Reference](https://developers.notion.com/reference/block).

## Block Categories

### Text Blocks

Text-based content blocks for writing and formatting.

- **[Paragraph](blocks/paragraph.md)** - Basic text content
- **[Heading](blocks/heading.md)** - H1, H2, H3 headings
- **[Quote](blocks/quote.md)** - Quoted text blocks
- **[Callout](blocks/callout.md)** - Highlighted information boxes
- **[Code](blocks/code.md)** - Syntax-highlighted code blocks

### List Blocks

Structured list content for organization.

- **[Bulleted List](blocks/bulleted-list.md)** - Unordered lists with bullets
- **[Numbered List](blocks/numbered-list.md)** - Ordered lists with numbers
- **[To Do](blocks/todo.md)** - Checkbox task lists

### Interactive Blocks

Blocks that provide interactive functionality.

- **[Toggle](blocks/toggle.md)** - Collapsible content sections
- **[Toggleable Heading](blocks/toggleable-heading.md)** - Collapsible headings

### Layout Blocks

Blocks for structuring page layout and organization.

- **[Divider](blocks/divider.md)** - Horizontal dividing lines
- **[Column List](blocks/column-list.md)** - Multi-column layouts
- **[Column](blocks/column.md)** - Individual columns
- **[Table](blocks/table.md)** - Structured data tables

### Files & Media

Rich content integration and file handling.

- **[Image](blocks/image.md)** - Image embeds and uploads
- **[Video](blocks/video.md)** - Video embeds (YouTube, Vimeo, etc.)
- **[PDF](blocks/pdf.md)** - PDF document embeds
- **[File](blocks/file.md)** - File attachments and downloads
- **[Embed](blocks/embed.md)** - Generic web content embeds

### Mathematical Blocks

Scientific and mathematical content.

- **[Equation](blocks/equation.md)** - LaTeX mathematical expressions

### Navigation Blocks

Page navigation and structure.

- **[Table of Contents](blocks/table-of-contents.md)** - Automatic page TOC
- **[Breadcrumb](blocks/breadcrumb.md)** - Navigation breadcrumbs

## Content Creation Examples

### Markdown Syntax Approach

````python
# Using direct markdown strings
content = """
[toc]

## Overview
This project provides **powerful features** for developers.

[callout](💡 **Tip:** Check our examples for best practices "💡")

## Features
- Real-time collaboration
- Advanced analytics
- Custom integrations

## Code Example
```python
from notionary import NotionPage
page = await NotionPage.from_page_name("My Page")
````

### Error Handling & Reliability

Notionary provides robust error handling for all content operations:

- **Text Length Validation** - Automatic truncation for API limits
- **Graceful Fallbacks** - Unsupported blocks convert to paragraphs
- **Retry Logic** - Automatic retries for network issues
- **Content Validation** - Ensures all blocks meet Notion requirements

## Block Reference

Explore the complete documentation for each block type:

**Text & Formatting:** [Paragraph](blocks/paragraph.md) • [Heading](blocks/heading.md) • [Quote](blocks/quote.md) • [Callout](blocks/callout.md) • [Code](blocks/code.md)

**Lists & Structure:** [Bulleted List](blocks/bulleted_list.md) • [Numbered List](blocks/numbered_list.md)

**Layout & Organization:** [Divider](blocks/divider.md) • [Column](blocks/column.md) • [Toggle](blocks/toggle.md) • [Table](blocks/table.md)

**Files & Media:** [Image](blocks/image.md) • [Video](blocks/video.md) • [PDF](blocks/pdf.md) • [File](blocks/file.md) • [Embed](blocks/embed.md)

**Math & Navigation:** [Equation](blocks/equation.md) • [Table of Contents](blocks/table_of_contents.md) • [Breadcrumb](blocks/breadcrumb.md)

## Next Steps

- **[Getting Started](getting-started.md)** - Set up your first Notionary project
- **[Features](features.md)** - Explore all platform capabilities
- **[Official Notion API](https://developers.notion.com/reference/block)** - Complete API reference
