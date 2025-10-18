# Callout

Visually highlight important information (tips, warnings, notes, emphasis). Supports inline rich text (see [Rich Text](./rich_text.md)) and nested child blocks with indentation.

## Syntax

### Inline Format
```markdown
[callout](Message text)
[callout](Message text "🔥")  // with custom emoji
```

### Block Format with Children
```markdown
[callout] Message text
    Indented child content
    - Nested list item

[callout] Message text "⚠️"
    Multiple child blocks
    can be nested here
```

If no emoji is provided a default (💡) is used.

## Examples

### Inline Format
```markdown
[callout](Remember to back up your data "⚠️")
[callout](Install **version 1.4** first "🚀")
[callout](Docs: [Reference](https://example.com) "📚")
[callout](This is a simple note)  // uses default emoji 💡
```

### Block Format with Nested Content
```markdown
[callout] Important Setup Steps "🔧"
    1. Install dependencies
    2. Configure environment
    - Check requirements

[callout] Warning
    Make sure to backup before proceeding!
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

## Reference

!!! info "Notion API Reference"
    For the official Notion API reference on callout blocks, see <a href="https://developers.notion.com/reference/block#callout" target="_blank">https://developers.notion.com/reference/block#callout</a>
