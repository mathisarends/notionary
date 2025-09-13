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

    NAME = "Jarvis Clipboard"

    try:
        page = await NotionPage.from_page_name(NAME)

        #  await page.post_comment("This is a **test comment** with _markdown_ formatting!")
        url = await page.set_external_icon(
            "https://storage.googleapis.com/snipd-public/book-cover-images/92282f00-f643-496f-8434-0d6278cd93ff.jpg?update_ts=1731053129"
        )
        print(f"✅ External icon set successfully! URL: {url}")

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
