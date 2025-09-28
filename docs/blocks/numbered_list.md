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
