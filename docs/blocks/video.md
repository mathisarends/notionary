# Video Blocks

Video blocks embed content from YouTube, Vimeo, or direct file URLs. Ideal for tutorials, demos, and training.

## Basic Syntax

```markdown
[video](https://youtube.com/watch?v=VIDEO_ID)
[video](https://vimeo.com/VIDEO_ID)
[video](https://example.com/video.mp4)
```

## Quick Examples

```markdown
## Product Demo

[video](https://youtube.com/watch?v=dQw4w9WgXcQ "New Features Overview")
```

```markdown
## Training Module

[video](https://vimeo.com/123456789 "Authentication Basics - 15 min")
```

```markdown
## Direct File

[video](https://cdn.example.com/tutorial.mp4 "Installation Walkthrough")
```

## Captions & Context

```markdown
[video](https://youtube.com/watch?v=api_tutorial "Duration: 15 min | Beginner Level")
```

## Programmatic Usage

### Using MarkdownBuilder

```python
from notionary import MarkdownBuilder

builder = (MarkdownBuilder()
    .h1("Developer Training Program")
    .h2("Module 1: Getting Started")
    .video("https://youtube.com/watch?v=intro123", "Introduction - 10 minutes")
    .paragraph("Key concepts covered:")
    .bulleted_list([
        "Platform overview",
        "Basic navigation",
        "Account setup"
    ])
    .h2("Module 2: API Fundamentals")
    .video("https://youtube.com/watch?v=api456", "API Basics - 15 minutes")
    .paragraph("Learn about:")
    .bulleted_list([
        "Authentication methods",
        "Making requests",
        "Handling responses"
    ])
)

print(builder.build())
```

## Related Blocks

- **[Image](image.md)** – For static visuals
- **[Audio](audio.md)** – For audio-only content
- **[File](file.md)** – For downloadable media
- **[Embed](embed.md)** – For other embeddable content
