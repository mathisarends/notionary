"""
# Notionary: Caption Syntax Test
===============================

Testing the new consistent caption syntax across all media blocks.
Perfect for verifying the unified behavior!
"""

import asyncio

from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Test the new caption syntax across different media blocks."""

    print("🚀 Notionary Caption Syntax Test")
    print("=" * 40)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        markdown = """
        **Bold** mit (blue:blauem Text) und $E=mc^2$ Gleichung
        (red_background:**Fett mit rotem Hintergrund**)
        Normale (green:grüne Farbe) im Text
        
        Das ist eine page @page[Wissen & Notizen]
        
        ---
        
        1. this is a test
        2. this is a fest
        3. this is a quest
        """

        # Test all media blocks with the MarkdownBuilder
        await page.append_markdown(markdown)

        print("✅ Successfully added all caption syntax examples!")

        content = await page.get_text_content()
        print(f"📄 Page content preview:\n{content}...")

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
