# Table

Organize data in rows and columns. Headers are the first row, separator is `|---|---|`, data rows follow. Cells support inline rich text (see [Rich Text](./rich_text.md)).

## Syntax

```markdown
| Header 1 | Header 2 | Header 3 |
| -------- | -------- | -------- |
| Cell 1   | Cell 2   | Cell 3   |
| Value A  | Value B  | Value C  |
```

## Examples

```markdown
| Product | Price | Status |
| ------- | ----- | ------ |
| Widget  | $10   | Active |
| Gadget  | $25   | Draft  |
```

With rich text:

```markdown
| Task            | Assignee    | Status      |
| --------------- | ----------- | ----------- |
| Design mockups  | @user[Jane] | ✅ Complete |
| API development | @user[Bob]  | 🔄 Progress |
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Comparison")
  .table(
    headers=["Product", "Price", "Rating"],
    rows=[
      ["Widget", "$10", "4.5/5"],
      ["Gadget", "$25", "4.8/5"]
    ]
  )
  .build())
```


## Reference

!!! info "Notion API Reference"
    For the official Notion API reference on table blocks, see <a href="https://developers.notion.com/reference/block#table" target="_blank">https://developers.notion.com/reference/block#table</a>
