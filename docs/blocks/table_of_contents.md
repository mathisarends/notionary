# Table of Contents

Auto‑generated navigation from page headings.

## Syntax

```markdown
[toc]
```

## Examples

```markdown
# User Guide

[toc]

## Getting Started

...

## Advanced Features

...

### Configuration

...
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h1("Documentation")
  .table_of_contents()
  .h2("Installation")
  .paragraph("Setup steps...")
  .h2("Usage")
  .paragraph("How to use...")
  .build())
```
