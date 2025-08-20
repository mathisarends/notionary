# Content Management

This guide covers reading, writing, and managing content in Notion pages using markdown operations.

## Append Content

Add new content to the end of existing page content:

```python
from notionary import NotionPage

page = await NotionPage.from_page_name("My Notes")

# Simple markdown string
await page.append_markdown("""
## New Section

Additional content goes here with **formatting**.

- Bullet point one
- Bullet point two
""")

# With options
await page.append_markdown(
    "## Updates\nLatest changes to the project.",
    prepend_table_of_contents=True,
    append_divider=True
)
```

## Replace Content

Replace all existing page content with new content:

```python
# Replace entire page content
await page.replace_content("""
# Fresh Start

This completely replaces all existing content.

## Getting Started
1. First step
2. Second step
3. Third step
""")

# With table of contents
await page.replace_content(
    "# Documentation\n\nComplete guide content here.",
    prepend_table_of_contents=True
)
```

## Clear Content

Remove all content from a page:

```python
# Clear all blocks from the page
result = await page.clear_page_content()
```

## Read Content

Get existing page content as markdown:

```python
# Get current page content
content = await page.get_text_content()
print(content)

# Roundtrip workflow: read, modify, write back
existing_content = await page.get_text_content()
updated_content = existing_content + "\n\n## New Addition\nExtra content here."
await page.append_markdown(updated_content)
```

## Builder Pattern

Use the builder API for programmatic content creation:

```python
# Builder pattern with callback function
await page.append_markdown(lambda builder: (
    builder
    .h1("Project Overview")
    .callout("Important note", "💡")
    .h2("Features")
    .bulleted_list(["Feature 1", "Feature 2", "Feature 3"])
    .divider()
    .h2("Timeline")
    .table(
        headers=["Phase", "Status", "Due Date"],
        rows=[
            ["Planning", "Complete", "2024-01-15"],
            ["Development", "In Progress", "2024-03-01"]
        ]
    )
))

# Builder creates markdown strings internally
await page.replace_content(lambda builder: (
    builder
    .h1("Documentation")
    .columns(
        lambda col: col.h3("Left").paragraph("Left column content"),
        lambda col: col.h3("Right").paragraph("Right column content")
    )
))
```

## Markdown Syntax

Notionary uses extended markdown syntax that gets converted to Notion blocks. The builder pattern generates valid markdown strings, but you can also write markdown directly:

```python
# Direct markdown - all standard markdown works
await page.append_markdown("""
# Heading 1
## Heading 2
### Heading 3

**Bold text** and _italic text_ with `inline code`.

- Bulleted lists
- Work as expected

1. Numbered lists
2. Are also supported

[Links](https://example.com) and standard formatting.
""")

# Extended syntax for Notion-specific blocks
await page.append_markdown("""
[callout](This is a callout with custom emoji "🚀")

+++ Collapsible Toggle
Content inside the toggle is hidden by default.
+++

::: columns
::: column
Left column content
:::
::: column
Right column content
:::
:::

| Table | Header |
|-------|--------|
| Cell  | Data   |
""")
```

## Supported Blocks

Notionary supports all Notion block types through markdown syntax. Each block type has specific syntax and can be created using either direct markdown or the builder pattern.

**Text Blocks:** [Paragraph](../blocks/paragraph.md) • [Heading](../blocks/heading.md) • [Quote](../blocks/quote.md) • [Callout](../blocks/callout.md) • [Code](../blocks/code.md)

**Lists:** [Bulleted List](../blocks/bulleted_list.md) • [Numbered List](../blocks/numbered_list.md)

**Layout:** [Divider](../blocks/divider.md) • [Column](../blocks/column.md) • [Toggle](../blocks/toggle.md) • [Table](../blocks/table.md)

**Media:** [Image](../blocks/image.md) • [Video](../blocks/video.md) • [File](../blocks/file.md) • [PDF](../blocks/pdf.md) • [Embed](../blocks/embed.md)

**Navigation:** [Table of Contents](../blocks/table_of_contents.md) • [Breadcrumb](../blocks/breadcrumb.md) • [Equation](../blocks/equation.md)

For complete syntax reference and examples, see the [Block Types documentation](../blocks/index.md).

## Related Documentation

- **[Page Overview](index.md)** - Core page functionality
- **[Block Types](../blocks/index.md)** - Complete syntax reference
- **[Page Customization](customization.md)** - Appearance and metadata
