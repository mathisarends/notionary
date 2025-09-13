"""
# Notionary: Caption Syntax Test
===============================

Testing the new consistent caption syntax across all media blocks.
Perfect for verifying the unified behavior!
"""

import asyncio
from notionary import NotionPage

PAGE = "Protocols: An Operating Manual for the Human Body"


async def main():
    """Test the new caption syntax across different media blocks."""

    NAME = "Notionary"

    try:
        page = await NotionPage.from_page_name(NAME)

        #  await page.post_comment("This is a **test comment** with _markdown_ formatting!")
        await page.post_comment("This is a test comment")

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
