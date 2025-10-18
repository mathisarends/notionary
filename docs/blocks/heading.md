Headings create structure. Three levels are supported: `#`, `##`, `###` (H1–H3).

## Standard

```python
markdown = """

# Main Section

## Sub Section

### Detail Section

"""
```

Inline rich text (bold, links, code, etc.) is supported inside the heading text (see [Rich Text](./rich_text.md)).

## Heading with Children

There are two ways to create a toggleable heading:

1) Raw Markdown: To create a toggleable heading, simply indent child content under any heading using four spaces per level. No delimiter is needed.

```markdown
# Collapsible Main Section
  Content inside the toggleable heading.
  Can contain multiple paragraphs and other blocks.
```

2) Builder: Any heading (`h1`, `h2`, `h3`) becomes toggleable when you provide children via the builder function.

```python
from notionary import MarkdownBuilder

markdown = (
  MarkdownBuilder()
    .h1("Guide")
    .h2("Intro")
    .paragraph("Overview text.")
    .h2("Advanced", lambda b: (
      b.paragraph("Hidden details")
       .code("print('ok')", language="python")
    ))
    .build()
)
```

## Reference

!!! info "Notion API Reference"
    For the official Notion API reference on heading blocks, see <a href="https://developers.notion.com/reference/block#headings" target="_blank">https://developers.notion.com/reference/block#headings</a>
