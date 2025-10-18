# Column

Side‑by‑side layout. A column group is started with a `columns` container; each child `column` holds arbitrary block content.

## Syntax (Builder)

```python
builder.columns(
  lambda col: col.h3("Left").paragraph("Left content"),
  lambda col: col.h3("Right").paragraph("Right content")
)
```

With explicit width ratios (must add to 1.0):

```python
builder.columns(
  lambda col: col.h3("Main").paragraph("70% width"),
  lambda col: col.h3("Sidebar").paragraph("30% width"),
  width_ratios=[0.7, 0.3]
)
```

## Syntax (Raw Markdown)

```
::: columns
::: column
Left content
:::
::: column
Right content
:::
:::
```

You can nest bulleted and numbered lists inside columns using indentation:

```
::: columns
::: column
Features:
  - Real-time collaboration
  - Advanced analytics
  - Custom integrations
:::
::: column
Steps:
  1. Download installer
  2. Run setup wizard
  3. Configure settings
:::
:::
```

Lists can be arbitrarily nested using indentation, and both bulleted and numbered lists work inside columns.

With width ratios:

```
::: columns
::: column 0.7
Main
:::
::: column 0.3
Sidebar
:::
:::
```

Rules:

- Container starts with `::: columns` and ends with a lone `:::`.
- Each column starts with `::: column` or `::: column <ratio>` and ends with `:::`.
- Accepted ratio forms: `.5`, `0.5`, `0.25`, `1.0` (plain `1` is ignored and treated as no ratio).
- Omitted / invalid ratios fall back to equal width distribution.
- Order defines horizontal ordering (first = leftmost).

Example invalid builder usage (raises):

```python
builder.columns(
  lambda c: c.paragraph("Left"),
  lambda c: c.paragraph("Right"),
  width_ratios=[0.55, 0.5]  # ValueError: width ratios must sum to 1.0
)
```

## Examples

Two‑column layout:

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Comparison")
  .columns(
    lambda l: l.h3("Before").paragraph("Old approach."),
    lambda r: r.h3("After").paragraph("New approach.")
  )
  .build())
```

Three‑column with ratios:

```python
markdown = (MarkdownBuilder()
  .columns(
    lambda nav: nav.h4("Navigation").bulleted_list(["Home", "About"]),
    lambda main: main.h2("Content").paragraph("Main article."),
    lambda ads: ads.h4("Ads").paragraph("Advertisement."),
    width_ratios=[0.2, 0.6, 0.2]
  )
  .build())
```

## Reference

!!! info "Notion API Reference"
    For the official Notion API reference on column and column-list blocks, see <a href="https://developers.notion.com/reference/block#column-list-and-column" target="_blank">https://developers.notion.com/reference/block#column-list-and-column</a>
