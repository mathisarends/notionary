"""
# Notionary: Caption Syntax Test
===============================

Testing the new consistent caption syntax across all media blocks.
Perfect for verifying the unified behavior!
"""

import asyncio
from notionary import NotionPage


async def main():
    """Test the new caption syntax across different media blocks."""

    print("🚀 Notionary Caption Syntax Test")
    print("=" * 40)

    try:
        page = await NotionPage.from_url(
            "https://www.notion.so/How-to-Set-Achieve-Massive-Goals-Alex-Honnold-269389d57bd3813aa5fdef5040d00748?v=1af389d57bd3812ea9b6000cd63ced14&source=copy_link"
        )

        episode_link = await page.get_options_for_property_by_name("Thema")
        print("episode_link", episode_link)

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
