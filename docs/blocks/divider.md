# Divider Blocks

Divider blocks create horizontal lines to visually separate content sections.

## Syntax

```markdown
---
```

## Usage

### Section Separation

```markdown
## Introduction

Welcome to our platform.

---

## Getting Started

Follow these steps...

---

## Advanced Features

Learn about advanced capabilities.
```

### Content Organization

```markdown
# User Guide

Basic setup information here.

---

**Advanced Configuration**

Complex setup details here.

---

**Troubleshooting**

Common issues and solutions.
```

## Programmatic Usage

```python
from notionary.blocks.divider import DividerMarkdownNode

# Create divider
divider = DividerMarkdownNode()
markdown = divider.to_markdown()

# Add between content sections
content = """
## Section 1
Content here.

---

## Section 2
More content here.
"""
await page.append_markdown(content)
```

## Visual Effect

Dividers appear as:

- **Horizontal line** across page width
- **Subtle styling** that matches theme
- **Spacing** above and below for visual breathing room
- **Responsive** design that works on all screen sizes

## Best Practices

- **Logical breaks**: Use between distinct topics
- **Don't overuse**: Too many dividers create visual clutter
- **Alternative to headings**: When new heading isn't needed
- **Before important sections**: Emphasize key content

## Common Use Cases

- **Long articles** - Break up dense content
- **Multi-topic pages** - Separate different subjects
- **Before calls-to-action** - Emphasize important actions
- **Documentation** - Separate sections logically

## Related Blocks

- **[Heading](heading.md)** - For structured content organization
- **[Callout](callout.md)** - For highlighted section breaks
- **[Quote](quote.md)** - For emphasized content separation
