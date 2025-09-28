# Image

Display images with optional captions and alt text.

## Syntax

```markdown
[image](path/to/image.jpg)
[image](https://example.com/photo.jpg "Caption text")
```

## Examples

```markdown
[image](./assets/screenshot.png)
[image](https://example.com/diagram.svg "System architecture")
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Setup Guide")
  .image("./assets/interface.png", "Main dashboard view")
  .paragraph("Navigate using the sidebar.")
  .build())
```
