MARKDOWN_EXAMPLE = """
# Notionary Rich Markdown Demo

!> [💡] This example was automatically generated using the Notionary Python library.

<!-- spacer -->

## Text Formatting

You can use standard Markdown formatting:
- **Bold text** for emphasis
- *Italic text* for slight emphasis
- ~~Strikethrough~~ for outdated information
- `code` for technical terms
- [External links](https://github.com/yourusername/notionary)

<!-- spacer -->

Plus custom highlight formats:
- ==This is highlighted in yellow== (default)
- ==red:Important warning== that needs attention
- ==blue:Note:== Always share pages with your integration

<!-- spacer -->

## Rich Content Blocks

### Callouts

!> {blue_background} [💧] **Tip:** Callouts are great for tips and important information

!> {yellow_background} [⚠️] **Warning:** Make sure your page is shared with your integration

!> {green_background} [✅] **Success:** Your content has been updated successfully

### Toggles

+++ How to use NotionPageManager
  1. Initialize with `page_manager = NotionPageManager(url="your-notion-url")`
  2. Update metadata with `set_title()`, `set_page_icon()`, etc.
  3. Add content with `replace_content()` or `append_markdown()`
  4. Don't forget to `await page_manager.close()` when finished

+++ Custom Markdown Features
  Notionary supports many Notion-specific features:
  - Callouts with custom colors
  - Toggles for collapsible content
  - Rich embeds
  - And much more!

<!-- spacer -->

## Task Management

Here's a project plan implemented as interactive to-dos:

- [x] Initialize project
- [x] Create basic structure
- [ ] Implement advanced features
- [ ] Write documentation
- [ ] Release v1.0

### Project Timeline

| Phase | Deadline | Status |
| ----- | -------- | ------ |
| Planning | Jan 15 | Completed |
| Development | Feb 28 | In Progress |
| Testing | Mar 15 | Not Started |
| Release | Apr 1 | Not Started |

<!-- spacer -->

## Code Examples

```python
# Example: How to use NotionPageManager
from notionary.core.page.notion_page_manager import NotionPageManager

async def update_page():
    # Initialize with a page URL
    manager = NotionPageManager(url="https://notion.so/your-page")
    
    # Update page metadata
    await manager.set_title("Updated Page")
    await manager.set_page_icon(emoji="🚀")
    
    # Add rich content with custom Markdown
    await manager.replace_content("# New Page\\n\\nThis is **rich** content.")
    
    # Always close when done
    await manager.close()
```

```mermaid
flowchart TD
    A[Start] --> B{Has Notion API Token?}
    B -->|Yes| C[Create NotionPageManager]
    B -->|No| D[Set up Notion integration]
    C --> E[Update page content]
    E --> F[Close connection]
    F --> G[End]
```

<!-- spacer -->

## Features List

### Key Features
- Easy-to-use Python API
- Rich Markdown support
- Async functionality
- Comprehensive documentation

### Benefits
- Save time with automation
- Create consistent pages
- Integrate with your applications
- Simplify content management

<!-- spacer -->

## Embedded Content

### Helpful Resources

[bookmark](https://developers.notion.com "Notion API Documentation" "Official Notion API documentation and guides")

[bookmark](https://github.com/yourusername/notionary "Notionary on GitHub" "Source code and documentation for the Notionary library")

---

## Conclusion

This example demonstrates how you can use Notionary to create rich, interactive Notion pages with a simple Markdown-like syntax. The library handles all the complex API interactions, letting you focus on creating great content.

> [background:blue] Notionary makes Notion automation easy and powerful!

<!-- spacer -->

==green:Next steps:== Explore the Notionary documentation to discover more features and possibilities.

+++ Togggle
  - [ ] Read the documentation
  - [ ] Try out the examples
  - [ ] Build your own Notion automation scripts
"""
