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

    # 1. Find a page by its name (most convenient method)
    print("Searching for page by name...")
    page = await NotionPageFactory.from_page_name(YOUR_PAGE_NAME)

    icon = await page.get_icon()
    title = await page.get_title()
    url = await page.get_url()
    
    print(f"✅ Found: {title} {icon}")
    print("Gop od URL:", url)


if __name__ == "__main__":
    print("🚀 Starting Notionary URL Lookup Example...")
    found_page = asyncio.run(main())
    print("✅ Example finished!")
