# Paragraph Blocks

Paragraph blocks are the foundation of content in Notion and serve as the **fallback block type** when no other specialized syntax matches. They support rich text formatting including bold, italic, strikethrough, underline, inline code, and links.

## Syntax

```markdown
This is a basic paragraph with **bold**, _italic_, and `inline code`.

You can also include [links](https://example.com) and ~~strikethrough~~ text.

Multiple paragraphs are separated by blank lines.
```

## Rich Text Formatting

### Text Styles

```markdown
**Bold text** - Important emphasis
_Italic text_ - Subtle emphasis
**Underlined text** - Underlined content
~~Strikethrough~~ - Deleted content
`Inline code` - Code snippets
```

### Links

```markdown
[Link text](https://example.com)
[Link with title](https://example.com "Hover title")
```

### Mentions

```markdown
@[page-id-here] - Link to another page
@user(user-id) - Mention a user
@db(database-id) - Reference a database
```

## Programmatic Usage

### Creating Paragraphs

```python
from notionary.blocks.paragraph import ParagraphMarkdownNode

# Simple paragraph
paragraph = ParagraphMarkdownNode(text="Hello, world!")
markdown = paragraph.to_markdown()

# Rich text paragraph
rich_paragraph = ParagraphMarkdownNode(
    text="Visit our **website** at [example.com](https://example.com)"
)
```

### Using with Pages

```python
import asyncio
from notionary import NotionPage

async def add_content():
    page = await NotionPage.from_page_name("My Page")

    # Add single paragraph
    await page.append_markdown("This is a simple paragraph.")

    # Add formatted paragraph
    formatted_text = """
    This paragraph includes **bold text**, _italic text_,
    and a [link](https://example.com) for reference.
    """
    await page.append_markdown(formatted_text)

asyncio.run(add_content())
```

### With MarkdownBuilder

```python
from notionary.markdown import MarkdownBuilder

def create_content():
    builder = MarkdownBuilder()
    builder.paragraph("Introduction paragraph with key information.")
    builder.paragraph("Second paragraph with **emphasis** and details.")
    return builder.build()

# Use with page
await page.replace_content(create_content)
```

## Advanced Features

### Color Support

```python
from notionary.blocks.paragraph import ParagraphBlock
from notionary.blocks.types import BlockColor

# Programmatically set paragraph color
paragraph_block = ParagraphBlock(
    rich_text=[...],
    color=BlockColor.BLUE_BACKGROUND
)
```
