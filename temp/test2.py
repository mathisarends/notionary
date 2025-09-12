"""
# Notionary: Caption Syntax Test
===============================

Testing the new consistent caption syntax across all media blocks.
Perfect for verifying the unified behavior!
"""

import asyncio
from notionary import NotionPage, MarkdownBuilder

PAGE = "Protocols: An Operating Manual for the Human Body"


async def main():
    """Test the new caption syntax across different media blocks."""

    NAME = "Jarvis Clipboard"

    try:
        page = await NotionPage.from_page_name(NAME)

        markdown = (
            MarkdownBuilder()
            .paragraph("This is a test paragraph.")
            .space()
            .paragraph("Another paragraph after a space.")
            .build()
        )
        
        await page.append_markdown(markdown)
        
        text_content = await page.get_text_content()
        print("Current page content:", text_content)

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
