"""
# Notionary: Page Lookup by URL Example
======================================

This example demonstrates how to load a Notion page using its full URL.
This is useful when you already have the full link (e.g. from sharing).

IMPORTANT: Replace the URL string below with the actual link to your Notion page.
"""

import asyncio
from notionary import NotionPageFactory

async def main():
    """Demonstrate how to create a NotionPage from a full Notion URL."""
    print("🔗 Looking up Notion page by URL...")
    print("===================================")

    try:
        url = "https://www.notion.so/Jarvis-Clipboard-1a3389d57bd380d7a507e67d1b25822c"

        page = await NotionPageFactory.from_url(url)
        
        icon, title, page_url = await asyncio.gather(
            page.get_icon(),
            page.get_title(),
            page.get_url()
        )
        
        print(f"✅ Found: \"{title}\" {icon} → {page_url}")

    except Exception as e:
        print(f"❌ Error while loading page from URL: {e}")


if __name__ == "__main__":
    print("🚀 Starting Notionary URL Lookup Example...")
    asyncio.run(main())