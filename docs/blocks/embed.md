# Embed

Embed external content (YouTube, Twitter, etc.) directly in the page.

## Syntax

Captions are supported by adding a `[caption]` line immediately below the block.

```markdown
[embed](https://example.com)
[caption] Caption text
```

## Examples

```markdown
[embed](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
[caption] Product walkthrough

[embed](https://twitter.com/user/status/123456789)
[caption] Key announcement
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
