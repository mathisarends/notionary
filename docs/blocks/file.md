# File

Attach and reference files. Supports uploads and external links.

## Syntax

Captions are supported by adding a `[caption]` line immediately below the block.

```markdown
[file](path/to/file.pdf)
[caption] User manual
```

## Examples

```markdown
[file](./assets/specification.pdf)
[caption] Technical specification

[file](https://docs.example.com/api.pdf)
[caption] API Reference
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Resources")
  .file("./assets/manual.pdf", "Installation guide")
  .paragraph("Download and follow the steps.")
  .build())
```


!!! info "Notion API Reference"
    For the official Notion API reference on file blocks, see <a href="https://developers.notion.com/reference/block#file" target="_blank">https://developers.notion.com/reference/block#file</a>
