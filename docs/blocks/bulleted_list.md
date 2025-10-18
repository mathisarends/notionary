# Bulleted List

Unordered list with bullet points. Each item supports inline rich text (see [Rich Text](./rich_text.md)).

## Syntax

```markdown
- First item
- Second item
- Third item
```

Alternative markers: `*` or `+` instead of `-`.

## Examples

```markdown
- Real-time collaboration
- Advanced analytics
- 24/7 support
```

With rich text:

```markdown
- **Bold** important item
- Visit [docs](https://example.com)
- Ask @user[Jane] for details
```

Nested and mixed lists (using indentation):

```markdown
- Features
  1. Real-time collaboration
  2. Advanced analytics
  3. Custom integrations
- Roadmap
  - Q1: Stabilization
  - Q2: Performance
    1. Cache layer
    2. Query planner
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Features")
  .bulleted_list([
    "Real-time collaboration",
    "Advanced analytics",
    "Custom integrations"
  ])
  .build())
```

## Reference

!!! info "Notion API Reference"
    For the official Notion API reference on bulleted-list blocks, see <a href="https://developers.notion.com/reference/block#bulleted-list-item" target="_blank">https://developers.notion.com/reference/block#bulleted-list-item</a>
