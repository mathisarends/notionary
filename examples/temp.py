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

        markdown_content = """
+++ This is a toggle block
   This is the content of the toggle block.
        """

        await page.append_markdown(markdown_content)


    except Exception as e:
        print(f"❌ Error while loading page from URL: {e}")


if __name__ == "__main__":
    print("🚀 Starting Notionary URL Lookup Example...")
    found_page = asyncio.run(main())
