# Callout Blocks

Callout blocks create visually prominent information boxes perfect for highlighting important content, tips, warnings, and notes.

## Syntax

```markdown
[callout](Important information goes here)
[callout](Custom message "🔥")
[callout](Warning message "⚠️")
```

## Basic Usage

### Default Callout

```markdown
[callout](This creates a callout with the default light bulb emoji)
```

### Custom Emoji

```markdown
[callout](Success message "✅")
[callout](Warning information "⚠️")
[callout](Error details "❌")
[callout](Info note "ℹ️")
[callout](Tip or trick "💡")
```

### Rich Text Support

```markdown
[callout](This callout includes **bold text**, _italic text_, and `code` "🚀")
[callout](Visit our [documentation](https://docs.example.com) for more details "📚")
```

## Programmatic Usage

### Creating Callouts

```python
from notionary.blocks.callout import CalloutMarkdownNode

# Basic callout
callout = CalloutMarkdownNode(
    text="Important information",
    emoji="💡"
)

# Rich text callout
rich_callout = CalloutMarkdownNode(
    text="Check out our **new features** at [example.com](https://example.com)",
    emoji="🚀"
)

markdown = callout.to_markdown()
```

### Using with Pages

```python
import asyncio
from notionary import NotionPage

async def add_callouts():
    page = await NotionPage.from_title("My Guide")

    # Add tip callout
    await page.append_markdown('[callout](💡 **Pro Tip:** Save time with shortcuts "💡")')

    # Add warning
    await page.append_markdown('[callout](⚠️ **Warning:** Backup your data first "⚠️")')

asyncio.run(add_callouts())
```

### With MarkdownBuilder

```python
from notionary.markdown import MarkdownBuilder

def create_guide():
    builder = MarkdownBuilder()

    builder.heading("Setup Guide", level=1)
    builder.callout("Before starting, ensure you have admin access", emoji="🔑")
    builder.paragraph("Follow these steps...")
    builder.callout("Remember to test in staging first!", emoji="⚠️")

    return builder.build()

await page.replace_content(create_guide)
```
