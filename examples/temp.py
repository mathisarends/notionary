"""
# Notionary: Page Lookup Example
===============================

This example demonstrates how to locate an existing Notion page
using the NotionPageFactory.

It showcases the easiest way to access a page by its name,
but also mentions alternatives like lookup by ID or URL.

IMPORTANT: Replace "Jarvis fitboard" with the actual name of your page.
The factory uses fuzzy matching to find the closest match.
"""

import asyncio
from notionary import NotionPageFactory

YOUR_PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Demonstrates various ways to find a Notion page."""

    try:
        print("Searching for page by name...")
        page = await NotionPageFactory.from_page_name(YOUR_PAGE_NAME)

        icon, title, url = await asyncio.gather(
            page.get_icon(), page.get_title(), page.get_url()
        )

        print(f'✅ Found: "{title}" {icon} → {url}')

# TODO: Gucken wie das hier gelesen wird

        markdown_content = """
# Main Title 

## Section Title

### Subsection Title

This is a simple paragraph with **bold** and *italic* formatting. You can also include [links](https://example.com) or `inline code`.

- First item
- Second item
- Third item

1. First step
2. Second step
3. Third step

> This is a simple blockquote
> This is a multi-line quote
> that continues on the next line

!> [💡] Tip: Add emoji that matches your content's purpose

![Data visualization showing monthly trends](https://example.com/chart.png)

@[How to use this feature](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

$[Podcast Episode](https://storage.googleapis.com/audio_summaries/ep_ai_summary_127d02ec-ca12-4312-a5ed-cb14b185480c.mp3)

<embed:Course materials>(https://drive.google.com/file/d/123456/view)

[bookmark](https://github.com "GitHub" "Where the world builds software")

| Product | Price | Stock |
| ------- | ----- | ----- |
| Widget A | $10.99 | 42 |
| Widget B | $14.99 | 27 |

- [ ] Draft project proposal
- [x] Create initial timeline

+++ Toggle Title
| The research demonstrates **three main conclusions**:
| 1. First important point
| 2. Second important point

+## Collapsible Heading
| This content is hidden until expanded

---

```python
print('Hello, world!')
```

Check the meeting notes at @[1a6389d5-7bd3-80c5-9a87-e90b034989d0]
Deadline is @date[2023-12-31]


+++ Umsatzstatistiken
| Hier ist unsere Umsatzstatistik für Q2:
| 
| | Produkt | Umsatz | Gewinn |
| | ------- | ------ | ------ |
| | Produkt A | €10.000 | €4.000 |
| | Produkt B | €15.000 | €6.000 |
        """

        await page.append_markdown(markdown_content)

    except Exception as e:
        print(f"❌ Error while loading page from URL: {e}")


if __name__ == "__main__":
    print("🚀 Starting Notionary URL Lookup Example...")
    found_page = asyncio.run(main())
