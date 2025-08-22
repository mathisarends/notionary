"""
# Notionary: Simple Page Demo
============================

A quick demo showing basic page information retrieval.
Perfect for getting started with Notionary!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio

from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Simple demo of NotionPage basic getters."""

    print("🚀 Notionary Simple Demo")
    print("=" * 30)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        markdown = """
        [bookmark](https://example.com)(caption:A simple Test is whats left)
        """

        await page.append_markdown(markdown)
        print("didi it")
        
        content = await page.get_text_content()
        print(f"📄 Page content:\n{content}"    )

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
