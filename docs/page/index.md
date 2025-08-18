# NotionPage

The `NotionPage` class is the core interface for managing Notion pages in Notionary. It provides comprehensive functionality for reading, writing, and manipulating page content and metadata with full roundtrip capabilities.

## Core Features

### 🔄 Roundtrip Content Management

Read existing page content and seamlessly append new content while preserving formatting and structure.

### 📝 Rich Content Creation

Create complex layouts using either direct markdown syntax or the powerful MarkdownBuilder API.

### 🔍 Smart Page Discovery

Find pages by name using fuzzy matching, by ID, or by URL with intelligent search capabilities.

### ⚡ Async-First Design

Built for modern Python with full async/await support for optimal performance.

## Getting Started

### Creating NotionPage Instances

```python
from notionary import NotionPage

# Find page by name (fuzzy matching)
page = await NotionPage.from_page_name("My Project Documentation")

# Get page by ID
page = await NotionPage.from_page_id("12345678-1234-1234-1234-123456789012")

# Load page from URL
page = await NotionPage.from_url("https://notion.so/workspace/page-id")
```

## Reading Content

### Get Text Content

Extract the complete text content of a page as markdown:

```python
# Get all page content as markdown
content = await page.get_text_content()
print(content)
```

**Output Example:**

```markdown
# Project Overview

This is the main documentation for our project.

## Features

- Real-time collaboration
- Advanced analytics
- Custom integrations

[callout](💡 **Important:** Check the API documentation "💡")
```

### Roundtrip Workflow

The true power of Notionary lies in its roundtrip capabilities - read existing content, analyze it, and append new content seamlessly:

```python
# 1. Read existing content
existing_content = await page.get_text_content()
print(f"Current content:\n{existing_content}")

# 2. Analyze and append based on existing content
if "## Status" not in existing_content:
    await page.append_markdown("""
    ## Status

    [callout](✅ **Updated:** Documentation reviewed and approved "✅")

    ### Recent Changes
    - Added API examples
    - Updated installation guide
    - Fixed formatting issues
    """)

# 3. Read updated content
updated_content = await page.get_text_content()
print(f"Updated content:\n{updated_content}")
```

## Writing Content

### Append Markdown Content

Add new content to the end of an existing page:

```python
# Simple text addition
await page.append_markdown("""
# New Section

This content will be added to the end of the page.

## Features
- Easy integration
- Powerful API
""")

# With additional options
await page.append_markdown(
    content="## Table of Contents\n\nThis section covers...",
    prepend_table_of_contents=True,  # Add TOC at the beginning
    append_divider=True              # Add separator line
)
```

### Replace Complete Content

Replace the entire page content with new content:

```python
await page.replace_content("""
# Fresh Start

This completely replaces all existing content.

[callout](🎉 **New:** Completely refreshed documentation "🎉")

## Getting Started
1. Install the package
2. Set up authentication
3. Create your first page
""")
```

### Using MarkdownBuilder API

For programmatic content creation, use the powerful MarkdownBuilder:

```python
# Builder pattern with callback function
await page.append_markdown(lambda builder: (
    builder
    .h1("API Documentation")
    .callout("📚 **Complete Guide:** Everything you need to know", "📚")
    .h2("Authentication")
    .code("import os\ntoken = os.getenv('NOTION_TOKEN')", "python")
    .h2("Basic Usage")
    .columns(
        lambda col: (col
            .h3("Reading Pages")
            .code("page = await NotionPage.from_page_name('My Page')", "python")
            .bulleted_list([
                "Fuzzy name matching",
                "Smart search results",
                "Error handling included"
            ])
        ),
        lambda col: (col
            .h3("Writing Content")
            .code("await page.append_markdown('# New content')", "python")
            .bulleted_list([
                "Markdown syntax support",
                "Rich block types",
                "Builder API available"
            ])
        )
    )
))
```

## Advanced Content Patterns

### Conditional Content Updates

```python
# Read and analyze existing content
current_content = await page.get_text_content()

# Add content based on what's already there
if "## Changelog" not in current_content:
    await page.append_markdown("""
    ## Changelog

    ### v1.0.0 - Initial Release
    - Basic page management
    - Content reading and writing
    - Markdown support
    """)
else:
    # Append to existing changelog
    await page.append_markdown("""
    ### v1.1.0 - Enhanced Features
    - Added MarkdownBuilder API
    - Improved error handling
    - Better documentation
    """)
```

### Content Templates

```python
def create_project_template(project_name: str, team_members: list[str]):
    """Generate a standardized project page template"""

    return lambda builder: (
        builder
        .h1(f"{project_name} - Project Overview")
        .callout(f"🚀 **Project:** {project_name} documentation", "🚀")

        .h2("Team Members")
        .bulleted_list(team_members)

        .h2("Project Status")
        .table(
            headers=["Phase", "Status", "Due Date"],
            rows=[
                ["Planning", "✅ Complete", "2024-01-15"],
                ["Development", "🔄 In Progress", "2024-02-28"],
                ["Testing", "⏳ Pending", "2024-03-15"]
            ]
        )

        .h2("Resources")
        .columns(
            lambda col: (col
                .h3("Documentation")
                .bulleted_list([
                    "[API Reference](link)",
                    "[User Guide](link)",
                    "[Examples](link)"
                ])
            ),
            lambda col: (col
                .h3("Development")
                .bulleted_list([
                    "[GitHub Repository](link)",
                    "[Issue Tracker](link)",
                    "[CI/CD Pipeline](link)"
                ])
            )
        )
    )

# Use the template
await page.replace_content(
    create_project_template("Notionary", ["Alice", "Bob", "Carol"])
)
```

### Dynamic Content Generation

```python
async def update_project_status(page: NotionPage, status_data: dict):
    """Update project status while preserving existing content"""

    # Read current content to preserve it
    existing_content = await page.get_text_content()

    # Generate status update
    status_section = lambda builder: (
        builder
        .divider()
        .h2("📊 Status Update")
        .callout(f"**Last Updated:** {status_data['date']}", "📅")
        .table(
            headers=["Metric", "Current", "Target", "Status"],
            rows=[
                ["Completion", f"{status_data['completion']}%", "100%",
                 "📈 On Track" if status_data['completion'] > 75 else "⚠️ Behind"],
                ["Budget", f"${status_data['budget_used']}K", f"${status_data['budget_total']}K",
                 "💰 Under Budget" if status_data['budget_used'] < status_data['budget_total'] else "💸 Over Budget"]
            ]
        )
    )

    # Append status update
    await page.append_markdown(status_section)

    # Return updated content for verification
    return await page.get_text_content()

# Usage
status_data = {
    "date": "2024-01-15",
    "completion": 85,
    "budget_used": 150,
    "budget_total": 200
}

updated_content = await update_project_status(page, status_data)
```

## Block Types Reference

Notionary supports all Notion block types through both markdown syntax and the MarkdownBuilder API. For complete documentation of available blocks, see:

**📚 [Block Documentation](../blocks/index.md)** - Complete reference for all supported block types

### Quick Block Examples

```python
# Text and formatting blocks
await page.append_markdown("""
# Heading
Regular paragraph text with **bold** and _italic_ formatting.

[callout](💡 **Pro Tip:** Use callouts for important information "💡")

> This is a quote block for emphasized text
""")

# Lists and structure
await page.append_markdown("""
## Features
- Bulleted list item
- Another item
- Third item

## Steps
1. First step
2. Second step
3. Third step
""")

# Layout and organization
await page.append_markdown("""
::: columns
::: column
### Left Column
Content for the left side
:::
::: column
### Right Column
Content for the right side
:::
:::

---

## Data Table
| Name | Role | Status |
|------|------|--------|
| Alice | Dev | Active |
| Bob | Designer | Active |
""")

# Rich media and interactive content
await page.append_markdown("""
[image](https://example.com/screenshot.png "Application Screenshot")

[video](https://youtube.com/watch?v=demo123 "Product Demo")

+++ Advanced Configuration
This content is collapsible and perfect for detailed information
that doesn't need to be visible by default.
+++
""")
```

## Page Metadata Management

### Basic Properties

```python
# Get page information
print(f"Title: {page.title}")
print(f"ID: {page.id}")
print(f"URL: {page.url}")
print(f"Emoji: {page.emoji_icon}")

# Update page title
await page.set_title("Updated Project Documentation")

# Set page icon
await page.set_emoji_icon("📚")
await page.set_external_icon("https://example.com/icon.png")

# Manage page cover
await page.set_cover("https://example.com/cover.jpg")
await page.set_random_gradient_cover()
```

### Database Properties

For pages in databases, manage custom properties:

```python
# Get property value
status = await page.get_property_value_by_name("Status")
priority = await page.get_property_value_by_name("Priority")

# Set property values
await page.set_property_value_by_name("Status", "In Progress")
await page.set_property_value_by_name("Priority", "High")

# Work with relation properties
related_pages = await page.get_property_value_by_name("Related Projects")
await page.set_relation_property_values_by_name("Related Projects", ["Project A", "Project B"])

# Get available options for select properties
status_options = await page.get_options_for_property_by_name("Status")
print(f"Available statuses: {status_options}")
```

## Error Handling and Best Practices

### Robust Error Handling

```python
try:
    page = await NotionPage.from_page_name("My Page")
    content = await page.get_text_content()

    await page.append_markdown("""
    ## New Section
    Additional content here
    """)

except ValueError as e:
    print(f"Page not found: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Performance Optimization

```python
# Batch multiple content updates
content_updates = [
    "## Section 1\nContent for section 1",
    "## Section 2\nContent for section 2",
    "## Section 3\nContent for section 3"
]

# Combine into single append operation
combined_content = "\n\n".join(content_updates)
await page.append_markdown(combined_content)

# Use builder for complex programmatic content
await page.append_markdown(lambda builder: (
    builder
    .h1("Batch Update")
    .paragraph("Multiple sections added efficiently:")
    .numbered_list([
        "Section 1 - Overview",
        "Section 2 - Details",
        "Section 3 - Conclusion"
    ])
))
```

## Complete Roundtrip Example

Here's a comprehensive example showing the full roundtrip capability:

```python
async def maintain_project_documentation():
    """Complete example of roundtrip page management"""

    # 1. Find the project page
    page = await NotionPage.from_page_name("Project Alpha Documentation")

    # 2. Read existing content to understand current state
    existing_content = await page.get_text_content()
    print(f"Current page has {len(existing_content)} characters")

    # 3. Analyze content and make decisions
    needs_status_section = "## Status" not in existing_content
    needs_changelog = "## Changelog" not in existing_content
    has_team_section = "## Team" in existing_content

    # 4. Conditionally add missing sections
    if needs_status_section:
        await page.append_markdown(lambda builder: (
            builder
            .h2("📊 Project Status")
            .callout("✅ **Status:** On track for Q1 delivery", "✅")
            .table(
                headers=["Phase", "Progress", "Due Date"],
                rows=[
                    ["Design", "100%", "2024-01-15"],
                    ["Development", "75%", "2024-02-28"],
                    ["Testing", "25%", "2024-03-15"]
                ]
            )
        ))

    if needs_changelog:
        await page.append_markdown("""
        ## 📝 Changelog

        ### 2024-01-20
        - Added status tracking
        - Updated team information
        - Improved documentation structure
        """)

    # 5. Update team section if it exists
    if has_team_section:
        await page.append_markdown("""
        ### New Team Member
        - **John Smith** - Backend Developer (joined 2024-01-20)
        """)
    else:
        await page.append_markdown(lambda builder: (
            builder
            .h2("👥 Team")
            .columns(
                lambda col: (col
                    .h3("Development Team")
                    .bulleted_list([
                        "**Alice Johnson** - Lead Developer",
                        "**Bob Wilson** - Frontend Developer",
                        "**Carol Davis** - Backend Developer"
                    ])
                ),
                lambda col: (col
                    .h3("Design Team")
                    .bulleted_list([
                        "**David Brown** - UI/UX Designer",
                        "**Emma Taylor** - Visual Designer"
                    ])
                )
            )
        ))

    # 6. Read final content to verify changes
    final_content = await page.get_text_content()
    print(f"Updated page now has {len(final_content)} characters")

    # 7. Update page metadata
    await page.set_emoji_icon("📚")
    await page.set_title("Project Alpha - Complete Documentation")

    return page

# Run the maintenance
page = await maintain_project_documentation()
```

## Next Steps

- **[Getting Started Guide](../getting-started.md)** - Set up your first Notionary project
- **[Block Reference](../blocks/index.md)** - Complete documentation for all block types
- **[Database Documentation](../database/index.md)** - Working with Notion databases
- **[Examples](../examples/)** - Real-world usage examples and patterns
