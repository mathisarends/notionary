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

PAGE_NAME = "The good enough job"


async def main():
    """Demonstrate page operations with Notionary."""
    print("📄 Notionary Page Example")
    print("========================")

    try:
        print(f"\n🔎 Finding page '{PAGE_NAME}'...")
        page = await NotionPage.from_page_name(PAGE_NAME)

        print("✨ Updating page properties...")

        content = await page.get_text_content()
        print(f"Current content: {content}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Starting Notionary page example...")
    asyncio.run(main())
    print("✅ Example completed!")
