"""
# Notionary: Page Management Example
===================================

This example demonstrates how to find and display Notion page information
using only getter methods (no modifications).

IMPORTANT: Replace PAGE_NAME with the name of an existing Notion page.
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboad"


async def main():
    """Demonstrate page getters with Notionary."""
    print("📄 Notionary Page Example (Getters Only)")
    print("========================")

    try:
        print(f"\n🔎 Finding page '{PAGE_NAME}'...")
        page = await NotionPage.from_page_name(PAGE_NAME)

        # Get current title for display
        current_title = await page.get_title()
        print(f"📌 Current title: {current_title}")

        page_content = await page.get_text_content()
        print(f"📜 Current content: {page_content}")

        page_url = await page.get_url()
        print(f"🔗 View page: {page_url}")

        page_icon = await page.get_icon()
        print(f"🏷️ Icon: {page_icon}")

        page_cover = await page.get_cover_url()
        print(f"🖼️ Cover URL: {page_cover}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Starting Notionary page example...")
    asyncio.run(main())
    print("✅ Example completed!")
