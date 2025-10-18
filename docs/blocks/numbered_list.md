# Numbered List

Ordered list with sequential numbers. Each item supports inline rich text (see [Rich Text](./rich_text.md)).

## Syntax

```markdown
1. First step
2. Second step
3. Third step
```

Numbers auto‑increment; you can use `1.` for all items.

## Examples

```markdown
1. Download the installer
2. Run setup wizard
3. Configure settings
```

With rich text:

```markdown
1. Check **requirements** first
2. Visit [docs](https://example.com)
3. Contact @user[Support] if needed
```

Nested and mixed lists (using indentation):

```markdown
1. Setup
  - Install dependencies
  - Configure environment
2. Tasks
  1. Implement feature A
    - Write unit tests
    - Update docs
  2. Review PRs
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Setup Steps")
  .numbered_list([
    "Download installer",
    "Run setup wizard",
    "Configure settings"
  ])
  .build())
```


## Reference

!!! info "Notion API Reference"
    For the official Notion API reference on numbered list blocks, see <a href="https://developers.notion.com/reference/block#numbered-list-item" target="_blank">https://developers.notion.com/reference/block#numbered-list-item</a>
