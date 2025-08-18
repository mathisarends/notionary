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
from notionary import MarkdownBuilder

builder = (MarkdownBuilder()
    .h2("Section 1")
    .paragraph("Content here.")
    .divider()
    .h2("Section 2")
    .paragraph("More content here.")
)

print(builder.build())
```

## Related Blocks

- **[Heading](heading.md)** - For structured content organization
- **[Callout](callout.md)** - For highlighted section breaks
- **[Quote](quote.md)** - For emphasized content separation
