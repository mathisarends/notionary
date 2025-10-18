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


## Reference

!!! info "Notion API Reference"
    For the official Notion API reference on table of contents blocks, see <a href="https://developers.notion.com/reference/block#table-of-contents" target="_blank">https://developers.notion.com/reference/block#table-of-contents</a>
