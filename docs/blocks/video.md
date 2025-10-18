# Video

Display video content from URLs or uploaded files with optional captions.

## Syntax

Captions are supported by adding a `[caption]` line immediately below the block.

```markdown
[video](https://example.com/video.mp4)
[caption] Setup walkthrough

[video](https://youtube.com/watch?v=abc123)
```

## Examples

```markdown
[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
[caption] Product demonstration

[video](./assets/demo.mp4)
[caption] Product demonstration

[video](https://vimeo.com/123456789)
[caption] Conference talk
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

## Reference

!!! info "Notion API Reference"
    For the official Notion API reference on video blocks, see <a href="https://developers.notion.com/reference/block#video" target="_blank">https://developers.notion.com/reference/block#video</a>
