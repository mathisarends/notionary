# Image

Display images with optional captions and alt text.

## Syntax

Captions are supported by adding a `[caption]` line immediately below the block.

```markdown
[image](path/to/image.jpg)
[caption] Caption text
```

## Examples

```markdown
[image](./assets/screenshot.png)
[caption] Main dashboard view

[image](https://example.com/diagram.svg)
[caption] System architecture
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
