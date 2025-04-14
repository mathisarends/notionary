import asyncio
from typing import Optional

from notionary.core.page.notion_page_manager import NotionPageManager


async def run_integration_test(page_id: Optional[str] = "integration-test-page-id"):
    """
    Runs an integration test that uses all Notion block elements to verify
    that the markdown conversion is working correctly.

    Args:
        page_id: Optional Notion page ID to use for the test
    """
    print(f"Starting integration test with page ID: {page_id}")

    content_manager = NotionPageManager(page_id=page_id)

    test_markdown = """# Notion Markdown Integration Test

This document demonstrates all supported Notion block types using our custom Markdown syntax.

## Headings

# Heading 1
## Heading 2
### Heading 3

## Paragraphs

This is a regular paragraph with **bold text**, *italic text*, and `inline code`.
It demonstrates the basic formatting capabilities.

Another paragraph with some __underlined__ text and ~~strikethrough~~ formatting.

## Callouts

!> [💡] This is a default callout with a light bulb emoji

!> {blue_background} [🔔] This is a blue callout with a bell emoji

!> {red_background} [⚠️] This is a warning callout with red background

## Code Blocks

Here's a Python code block:

```python
def hello_notion():
    print("Hello, Notion!")
    return "Integration test successful"
    
# Call the function
result = hello_notion()
print(f"Result: {result}")
```

And a JSON example:

```json
{
  "name": "Notion Integration Test",
  "successful": true,
  "blocks": [
    "heading",
    "paragraph",
    "callout",
    "code"
  ]
}
```

## Tables

Here's a table of Notion block types:

| Block Type | Markdown Syntax | Common Use Case |
| ---------- | --------------- | --------------- |
| Heading    | # Heading       | Section titles  |
| Paragraph  | Plain text      | Regular content |
| Callout    | !> [emoji] Text | Important notes |
| Code Block | ```language     | Code snippets   |
| Table      | \| Header \|    | Tabular data    |

## Bullet Lists

Here are some bullet points:

- First bullet item
- Second bullet item
  - Nested bullet item
  - Another nested item
- Third bullet item

## Todo Lists

Here's a todo list:

- [ ] Implement toggle blocks
- [x] Add support for callouts
- [ ] Test table rendering
- [x] Support code blocks
- [ ] Document all block types

## Toggle Blocks

+++ Click to expand this toggle
    This content is hidden inside a toggle block.
    It can contain multiple lines of text.
    
    You can even include formatted text like **bold** or *italic*.

+++ Another toggle with a code example
    ```python
    def nested_code():
        return "This code is inside a toggle block"
    ```

## Column Layout

::: columns
::: column
### First Column
This is the content in the first column.

- Bullet 1
- Bullet 2
:::
::: column
### Second Column
Content in the second column.

```python
def column_example():
    return "Code in column"
```
:::
::: column
### Third Column
The third column has different content.

!> [🎯] Callout in column
:::
:::

## Dividers

Above this is content.

---

Below this is more content.

## Images

Here's an example image:

![Notion Integration Test Image](https://images.unsplash.com/photo-1501504905252-473c47e087f8 "An example image")

## Bookmarks

[bookmark](https://notion.so "Notion Homepage" "The all-in-one workspace for notes, tasks, wikis, and databases")

[bookmark](https://github.com "GitHub")

## Quotes

> This is a regular quote block in Notion.
> It can span multiple lines.

> [background:blue] This is a quote with a blue background.
> You can use different colors.

## Videos

Here are some video examples:

@[Python Tutorial](https://www.youtube.com/watch?v=rfscVS0vtbw)

@[](https://youtu.be/dQw4w9WgXcQ)

@[Sample Video](https://example.com/sample-video.mp4)

## Complex Layout Example

::: columns
::: column
### Task List
- [x] Create headings
- [x] Add paragraphs
- [ ] Finish tables
- [ ] Add more examples

+++ Implementation Details
    The implementation uses custom Markdown syntax
    to generate Notion blocks through the API.
:::
::: column
### Code Example
```javascript
function notionExample() {
  console.log("Testing Notion integration");
  return {
    success: true,
    message: "Integration complete"
  };
}
```
:::
:::

!> [🏁] Integration test complete!
"""

    try:
        result = await content_manager.append_markdown(markdown=test_markdown)
        print(f"Integration test completed with result: {result}")

        return test_markdown
    except Exception as e:
        print(f"Error during integration test: {e}")
        raise


if __name__ == "__main__":
    JARVIS_CLIPBOARD_PAGE = "1a3389d5-7bd3-80d7-a507-e67d1b25822c"
    full_markdown = asyncio.run(run_integration_test(page_id=JARVIS_CLIPBOARD_PAGE))

    print("Integration test markdown saved to notion_integration_test.md")
