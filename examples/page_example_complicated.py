
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
        markdown_content = """
Bitte prüfe das Dokument: @[1a6389d5-7bd3-80c5-9a87-e90b034989d0]
Die Deadline ist @date[2023-12-31]
Die Daten sind in der DB @db[1a6389d5-7bd3-80e9-b199-000cfb3fa0b3]
"""
        await page_manager.append_markdown(markdown_content)
        # text = await page_manager.get_text()
        # print("Text from page:", text)

    except PageOperationError as e:
        print(f"❌ Error updating page: {e}")

if __name__ == "__main__":
    asyncio.run(main())