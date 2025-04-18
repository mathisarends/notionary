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

    url = "https://www.notion.so/Notionary-Rich-Markdown-Demo-1cd389d57bd381e58be9d35ce24adf3d?pvs=4"
    page = NotionPage(url=url)

    try:
        relations = await page.get_relation_values("Thema")
        print(f"Relations: {relations}")

    except PageOperationError as e:
        print(f"❌ Error updating page: {e}")


if __name__ == "__main__":
    asyncio.run(main())
