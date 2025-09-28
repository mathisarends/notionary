# Embed

Embed external content (YouTube, Twitter, etc.) directly in the page.

## Syntax

```markdown
[embed](https://example.com)
[embed](https://example.com "Caption text")
```

## Examples

```markdown
[embed](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
[embed](https://twitter.com/user/status/123456789 "Key announcement")
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Demo Video")
  .embed("https://www.youtube.com/watch?v=example", "Product walkthrough")
  .paragraph("See the features in action.")
  .build())
```
