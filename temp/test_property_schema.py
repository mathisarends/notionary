"""
# Notionary: Caption Syntax Test
===============================

Testing the new consistent caption syntax across all media blocks.
Perfect for verifying the unified behavior!
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Henningway Bridge"


async def main():
    """Test the new caption syntax across different media blocks."""

    print("🚀 Notionary Caption Syntax Test")
    print("=" * 40)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        values_for_thema = await page.get_property_value_by_name("Thema")
        print("Values for 'Thema':", values_for_thema)

        # working
        tags = await page.get_options_for_property_by_name("Tags")
        print("tags", tags)

        print("---")

        themes = await page.get_options_for_property_by_name("Thema")
        print("themes", themes)

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
