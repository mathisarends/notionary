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

        text_content = await page.get_text_content()

        # Display basic page information
        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"├── ID: {page.id}")
        print(f"└── Visit at: {page.url}")
        
        
        text_content = await page.get_text_content()
        print("text_content", text_content  )

        # Display truncated text content
        print("\n📄 Markdown Text Content (Preview):")
        if text_content:
            truncated_text = truncate_text(text_content)

            print(f"├── Length: {len(text_content)} characters")
            print(f"└── Preview: {repr(truncated_text)}")
        else:
            print("└── No text content found")

        print(f"\n✅ Successfully loaded page '{page.title}'!")

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


def truncate_text(text: str, max_length: int = 400) -> str:
    """Truncate text to specified length and add ellipsis if needed."""
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."


if __name__ == "__main__":
    asyncio.run(main())
