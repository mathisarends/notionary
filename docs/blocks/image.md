# Image Blocks

Image blocks embed visual content from URLs or files. Useful for documentation, tutorials, and diagrams.

## Basic Syntax

```markdown
[image](https://example.com/image.png)
[image](https://example.com/image.png "Caption text")
```

## Quick Examples

```markdown
## Dashboard Overview

[image](https://docs.example.com/screenshots/dashboard.png "Main dashboard overview")
```

```markdown
## Architecture Diagram

[image](https://docs.example.com/diagrams/architecture.svg "System Architecture")
```

```markdown
## Before/After Comparison

### Before

[image](https://updates.example.com/v1/old-ui.png "Old interface")

### After

[image](https://updates.example.com/v2/new-ui.png "New interface")
```

## Programmatic Usage

### Using MarkdownBuilder

```python
from notionary import MarkdownBuilder

builder = (MarkdownBuilder()
    .h1("User Interface Guide")
    .h2("Main Dashboard")
    .paragraph("When you log in, you'll see the main dashboard:")
    .image("https://docs.example.com/ui/dashboard.png", "Main dashboard overview")
    .h2("Settings Panel")
    .paragraph("Access account settings from the top-right menu:")
    .image("https://docs.example.com/ui/settings.png", "User settings panel")
)

print(builder.build())
```

## Related Blocks

- **[Video](video.md)** – For moving content
- **[File](file.md)** – For downloadable assets
- **[Callout](callout.md)** – For highlighting important visuals
- **[Toggle](toggle.md)** – For collapsible image groups
