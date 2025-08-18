# Table of Contents Blocks

Table of Contents blocks automatically generate navigation for page headings, providing quick access to different sections.

## Syntax

```markdown
[toc]
[toc](blue)
[toc](gray_background)
```

## Basic Usage

### Default Table of Contents

```markdown
# User Guide

[toc]

## Getting Started

Content about getting started...

## Advanced Features

Content about advanced features...

## Troubleshooting

Content about troubleshooting...
```

### Styled Table of Contents

```markdown
# API Documentation

[toc](blue_background)

## Authentication

API authentication methods...

## Endpoints

Available API endpoints...

## Error Handling

How to handle API errors...
```

## Color Options

```markdown
# Available colors

[toc] # Default
[toc](blue) # Blue text
[toc](blue_background) # Blue background
[toc](gray) # Gray text
[toc](gray_background) # Gray background
[toc](red) # Red text
[toc](green) # Green text
[toc](yellow) # Yellow text
[toc](orange) # Orange text
[toc](pink) # Pink text
[toc](purple) # Purple text
```

## Programmatic Usage

```python
from notionary.blocks.table_of_contents import TableOfContentsMarkdownNode

# Default TOC
toc = TableOfContentsMarkdownNode()

# Styled TOC
styled_toc = TableOfContentsMarkdownNode(color="blue_background")

# Add to page
await page.append_markdown("[toc]\n\n# Page Content")
```

## Automatic Generation

Table of contents automatically includes:

- **H1 headings** (# Level 1)
- **H2 headings** (## Level 2)
- **H3 headings** (### Level 3)
- **Clickable links** to each section
- **Nested structure** following heading hierarchy

## Behavior

- **Live updates**: TOC updates when headings change
- **Smooth scrolling**: Clicking links smoothly scrolls to sections
- **Mobile friendly**: Adapts to small screens
- **Keyboard accessible**: Supports keyboard navigation

## Best Practices

- **Place early**: Add TOC near the top of long documents
- **Long content**: Most useful for pages with 5+ sections
- **Clear headings**: Use descriptive heading text
- **Logical hierarchy**: Maintain proper heading levels

## Common Use Cases

- **Documentation** - Navigate through long guides
- **Articles** - Jump to specific sections
- **Reference pages** - Quick access to topics
- **Tutorials** - Skip to relevant steps

## Document Structure

```markdown
# Complete Guide

[toc]

## Prerequisites

What you need before starting...

## Installation

### Windows Setup

### macOS Setup

### Linux Setup

## Configuration

### Basic Settings

### Advanced Options

## Usage Examples

### Simple Example

### Advanced Example

## Troubleshooting

### Common Issues

### Support Resources
```

## Related Blocks

- **[Breadcrumb](breadcrumb.md)** - For site-level navigation
- **[Heading](heading.md)** - For document structure
- **[Divider](divider.md)** - For visual section breaks
- **[Link to Page](link-to-page.md)** - For manual page links
