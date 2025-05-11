"""
# Notionary: Page Management Example
===================================

This example demonstrates how to find and modify Notion pages,
including content updates, property changes, and formatting.

IMPORTANT: Replace PAGE_NAME with the name of an existing Notion page.
The factory will use fuzzy matching to find the closest match to this name.
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Meeting Notes"


async def main():
    """Demonstrate page operations with Notionary."""
    print("📄 Notionary Page Example")
    print("========================")

    try:
        print(f"\n🔎 Finding page '{PAGE_NAME}'...")
        page = await NotionPage.from_page_name(PAGE_NAME)

        print("✨ Updating page properties...")

        # Update icon and cover
        await page.set_emoji_icon("📝")
        await page.set_random_gradient_cover()

        # Get current title for display
        current_title = await page.get_title()
        print(f"📌 Current title: {current_title}")

        page_content = await page.get_text_content()
        print(f"📜 Current content: {page_content}")

        page_url = await page.get_url()
        print(f"🔗 View page: {page_url}")

        print("\n📋 Page structure:")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Starting Notionary page example...")
    asyncio.run(main())
    print("✅ Example completed!")
