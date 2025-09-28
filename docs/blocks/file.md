# File

Attach and reference files. Supports uploads and external links.

## Syntax

```markdown
[file](path/to/file.pdf)
[file](https://example.com/document.pdf "User manual")
```

## Examples

```markdown
[file](./assets/specification.pdf)
[file](https://docs.example.com/api.pdf "API Reference")
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
