"""
# Notionary: Caption Syntax Test
===============================

Testing the new consistent caption syntax across all media blocks.
Perfect for verifying the unified behavior!
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Angular Material Icons"


async def main():
    """Test the new caption syntax across different media blocks."""

    print("🚀 Notionary Caption Syntax Test")
    print("=" * 40)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        episode_link = await page.get_options_for_property_by_name("Thema")
        print("episode_link", episode_link)

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
