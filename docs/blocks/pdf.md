# PDF

Display PDF documents inline with optional captions.

## Syntax

```markdown
[pdf](path/to/document.pdf)
[pdf](https://example.com/manual.pdf "User guide")
```

## Examples

```markdown
[pdf](./assets/specification.pdf)
[pdf](https://docs.example.com/api.pdf "Complete API reference")
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
