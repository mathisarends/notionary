
"""
# Notionary: Rich Notion Page Example
=========================================

This example demonstrates how to create a feature-rich Notion page using the NotionPageManager
and custom Markdown extensions supported by Notionary.

## Features
- Connect to a Notion page using its URL
- Update page properties and metadata (title, icon, cover)
- Create rich content using custom Markdown syntax
- Showcase various Notion blocks (callouts, toggles, etc.)
"""

import asyncio
from notionary import NotionPage
from notionary.exceptions.database_exceptions import PageOperationError


async def main():
    """Create a rich Notion page showcasing various content blocks."""

    url = "https://www.notion.so/Jarvis-Clipboard-1a3389d57bd380d7a507e67d1b25822c"

    page_manager = NotionPage(url=url)

    try:
        # result = await page_manager.get_text()
        await page_manager.clear()

    except PageOperationError as e:
        print(f"❌ Error updating page: {e}")


if __name__ == "__main__":
    asyncio.run(main())
