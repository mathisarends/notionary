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
from notionary.blocks.embed import EmbedMarkdownNode

# Simple embed
embed = EmbedMarkdownNode(
    url="https://github.com/user/repo",
    caption="Project Repository"
)

# Add to page
await page.append_markdown('[embed](https://example.com "Live Demo")')
```

## Content Types

- **GitHub repositories** - Show repo information
- **CodePen/JSFiddle** - Interactive code examples
- **Figma designs** - Design prototypes
- **Google Maps** - Location embeds
- **Calendars** - Schedule integration
- **Forms** - Surveys and feedback

## Behavior

- **Responsive**: Adapts to container width
- **Interactive**: Maintains original functionality
- **Secure**: Sandboxed iframe implementation
- **Loading**: Shows placeholder while content loads

## Best Practices

- **Test embeds**: Verify content displays correctly
- **Mobile consideration**: Ensure embeds work on mobile
- **Loading time**: Consider impact on page performance
- **Fallback text**: Use descriptive captions

## Common Use Cases

- **Live demos** - Show working applications
- **Design previews** - Display prototypes
- **Documentation** - Embed external docs
- **Tools integration** - Include external services

## Related Blocks

- **[Video](video.md)** - For video-specific embeds
- **[Image](image.md)** - For static visual content
- **[Bookmark](bookmark.md)** - For link previews
- **[File](file.md)** - For downloadable content
