# Video

Display video content from URLs or uploaded files with optional captions.

## Syntax

```markdown
[video](https://example.com/video.mp4)
[video](./local/tutorial.mov "Setup walkthrough")
[video](https://youtube.com/watch?v=abc123)
```

## Examples

```markdown
[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
[video](./assets/demo.mp4 "Product demonstration")
[video](https://vimeo.com/123456789 "Conference talk")
```

## Builder

```python
from notionary.markdown import MarkdownBuilder

markdown = (MarkdownBuilder()
  .h2("Tutorial")
  .video("./assets/setup.mp4", "Installation guide")
  .paragraph("Follow along with the video.")
  .build())
```
