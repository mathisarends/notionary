# Heading Blocks

Heading blocks create hierarchical document structure with three levels (H1, H2, H3). They automatically generate table of contents when `[toc]` is used and provide the foundation for navigable documents.

## Standard Headings

### Syntax

```markdown
# Heading 1 - Main sections

## Heading 2 - Subsections

### Heading 3 - Sub-subsections
```

### Rich Text Support

```markdown
# **Bold** Main Title

## _Emphasized_ Section with [Links](https://example.com)

### `Code` Reference
```

## Toggleable Headings

Toggleable headings are collapsible sections that can contain nested content.

### Syntax

```markdown
+++# Collapsible Main Section
Content inside the toggleable heading.
Can contain multiple paragraphs and other blocks.
+++

+++## Collapsible Subsection
Nested content here.

- Bullet points
- More content
  +++

+++### Collapsible Sub-subsection
Detailed information in this section.
+++
```

### Example Usage

```markdown
+++## Configuration Options
Here are the available configuration settings:

- **API Key**: Your authentication token
- **Base URL**: The API endpoint URL
- **Timeout**: Request timeout in seconds

[callout](Remember to keep your API key secure! "🔐")
+++
```

## Table of Contents Integration

Headings automatically appear in the table of contents when using `[toc]`:

```markdown
# Documentation

[toc]

## Getting Started

### Installation

### Configuration

## API Reference

### Authentication

### Endpoints

+++## Advanced Topics
This section contains advanced configuration options.

### Custom Integrations

### Performance Tuning

+++
```

### Creating Toggleable Headings

```python
from notionary.blocks.toggleable_heading import ToggleableHeadingMarkdownNode

# Toggleable heading with nested content
toggleable = ToggleableHeadingMarkdownNode(
    text="Advanced Configuration",
    level=2,
    children=[
        ParagraphMarkdownNode("Configuration details here."),
        BulletedListMarkdownNode(["Option 1", "Option 2"])
    ]
)
```

### Using with Pages

```python
import asyncio
from notionary import NotionPage

async def create_structured_content():
    page = await NotionPage.from_title("Documentation")

    content = """
# API Guide

[toc]

## Overview
Core API functionality.

### Authentication
All requests require a valid API token.

+++## Advanced Topics
Detailed implementation notes.

### Rate Limiting
Maximum 3 requests per second.

### Error Handling
Comprehensive error management strategies.
+++
    """

    await page.replace_content(content)

asyncio.run(create_structured_content())
```

### With MarkdownBuilder

```python
from notionary.markdown import MarkdownBuilder

def create_documentation():
    builder = MarkdownBuilder()

    builder.heading("User Guide", level=1)
    builder.table_of_contents()

    builder.heading("Getting Started", level=2)
    builder.paragraph("First steps for new users.")

    builder.toggleable_heading("Advanced Settings", level=2, lambda toggle: (
        toggle.paragraph("Advanced configuration options:")
        .bulleted_list(["Custom themes", "API settings", "Security options"])
    ))

    return builder.build()

await page.replace_content(create_documentation)
```

## Best Practices

### Logical Hierarchy

```markdown
# ✅ Good - Clear progression

## Section A

### Subsection A.1

### Subsection A.2

# ❌ Avoid - Skipping levels

## Section A

#### Subsection (skipped H3)
```

### Descriptive Titles

```markdown
# ✅ Good - Specific and clear

## Authentication Setup

### Generating API Tokens

# ❌ Avoid - Vague

## Setup

### Step 1
```

### When to Use Toggleable Headings

Use toggleable headings for:

- **Optional details** - Advanced configuration, troubleshooting
- **Long sections** - Keep main content scannable
- **Reference material** - API details, examples that don't need to be always visible

```markdown
## Quick Start

Essential getting started steps.

+++## Troubleshooting
Detailed error resolution steps.
+++
```

## Related Blocks

- **[Table of Contents](table-of-contents.md)** - Auto-generated navigation from headings
- **[Toggle](toggle.md)** - General collapsible content blocks
- **[Paragraph](paragraph.md)** - Content under headings
- **[Divider](divider.md)** - Visual section breaks
