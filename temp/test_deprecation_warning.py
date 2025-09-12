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

    PAGE_NAME = "Jarvis Clipboard"

    try:
        page = await NotionPage.from_page_name(PAGE_NAME)

        cover_url = await page.get_cover_url()
        print("cover_url (deprecated):", cover_url)
        
        cover_url_new = page.cover_image_url
        print("cover_url_new (property):", cover_url_new)

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
