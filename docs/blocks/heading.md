Headings create structure. Three levels are supported: `#`, `##`, `###` (H1–H3). Keep them minimal and descriptive.

## Standard

```python
markdown = """

# Main Section

## Sub Section

### Detail Section

"""
```

Inline rich text (bold, links, code, etc.) is supported inside the heading text (see [Rich Text](./rich_text.md)).

## Toggleable Headings

Collapsed content regions that start with `+++` followed by a normal heading marker and end with a closing `+++` line.

Syntax:

```python
markdown = """
+++# Collapsible Main Section
Content inside the toggleable heading.
Can contain multiple paragraphs and other blocks.
+++
"""
```

## Builder Usage

```python
from notionary import MarkdownBuilder

markdown = (
    MarkdownBuilder()
      .h1("Guide")
      .h2("Intro")
      .paragraph("Overview text.")
      .toggleable_heading("Advanced", 2, lambda b: b.paragraph("Hidden details"))
      .build()
)
```
