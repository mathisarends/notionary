# PDF

Display PDF documents inline with optional captions.

## Syntax

Captions are supported by adding a `[caption]` line immediately below the block.

```markdown
[pdf](path/to/document.pdf)
[caption] User guide
```

## Examples

```markdown
[pdf](./assets/specification.pdf)
[caption] Complete API reference

[pdf](https://docs.example.com/api.pdf)
[caption] Complete API reference
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Documentation")
  .pdf("./assets/manual.pdf", "Installation guide")
  .paragraph("Follow the steps in the PDF above.")
  .build())
```
