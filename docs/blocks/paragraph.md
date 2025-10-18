Paragraph is the most fundamental block. If no other specific block syntax matches, text becomes a paragraph. Use it for normal narrative content and inline formatting.

Inline formatting, mentions, colors, equations: see the [Rich Text guide](./rich_text.md) for the complete syntax list.

## Basic Markdown

```markdown
This is a paragraph with **bold**, _italic_, `code`, a [link](https://example.com),
and ~~strikethrough~~ text.

Blank line → new paragraph.
```

## Mentions & Inline Rich Text

You can drop mentions directly inside paragraphs:

```markdown
Discuss with @user[Jane Doe] and link to @page[Architecture Overview].
Launch window: @date[2025-10-01–2025-10-07].
```

### Usage in markdown

```python
from notionary import MarkdownBuilder

markdown = """
Intro paragraph with context.
Follow‑up with **emphasis** and a [link](https://example.com)."
"""
await page.replace_content(lambda: builder.build())
```

### Usage with builder

```python
from notionary import MarkdownBuilder

builder = MarkdownBuilder() \
	.paragraph("Intro paragraph with context.") \
	.paragraph("Follow‑up with **emphasis** and a [link](https://example.com).")

await page.replace_content(lambda: builder.build())
```


## Reference

!!! info "Notion API Reference"
    For the official Notion API reference on paragraph blocks, see <a href="https://developers.notion.com/reference/block#paragraph" target="_blank">https://developers.notion.com/reference/block#paragraph</a>
