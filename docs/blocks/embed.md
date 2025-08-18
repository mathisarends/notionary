# Embed Blocks

Embed blocks integrate external web content directly into your Notion pages.

## Syntax

```markdown
[embed](https://example.com)
[embed](https://example.com "Caption text")
```

## Supported Content

### Web Pages

```markdown
[embed](https://github.com/user/repo)
[embed](https://codepen.io/user/pen/abc123)
[embed](https://figma.com/file/design-id)
```

### Interactive Tools

```markdown
[embed](https://replit.com/@user/project)
[embed](https://codesandbox.io/s/example)
[embed](https://observable.com/@user/notebook)
```

### Documentation

```markdown
[embed](https://api-docs.example.com "API Documentation")
[embed](https://status.example.com "Service Status")
```

## Programmatic Usage

```python
from notionary import MarkdownBuilder

builder = (MarkdownBuilder()
    .h1("Project Resources")
    .embed("https://github.com/user/repo", "Project Repository")
    .embed("https://codepen.io/user/pen/abc123", "Live Demo")
    .embed("https://figma.com/file/design-id", "Design Prototype")
)

print(builder.build())
```

## Related Blocks

- **[Video](video.md)** - For video-specific embeds
- **[Image](image.md)** - For static visual content
- **[Bookmark](bookmark.md)** - For link previews
- **[File](file.md)** - For downloadable content
