# Callout

Visually highlight important information (tips, warnings, notes, emphasis). Supports inline rich text (see [Rich Text](./rich_text.md)).

## Syntax

```markdown
[callout](Message text)
[callout](Message text "🔥") // with custom emoji
```

If no emoji is provided a default (💡) is used.

## Examples

```markdown
[callout](Remember to back up your data "⚠️")
[callout](Install **version 1.4** first "🚀")
[callout](Docs: [Reference](https://example.com) "📚")
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .callout("Before starting, ensure you have admin access", emoji="🔑")
  .paragraph("Follow these steps…")
  .callout("Test in staging first!", emoji="⚠️")
  .build())
```
