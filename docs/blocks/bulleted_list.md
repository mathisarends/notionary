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

## When To Use

- List features, benefits, requirements
- Unordered information (no sequence)
- Quick scannable points

## Related

- Numbered list: sequential items
- Todo: checkbox items
- Paragraph: continuous narrative
