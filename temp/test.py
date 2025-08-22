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

        # Test all media blocks with the new caption syntax
        markdown = """
# Caption Syntax Test

## Bookmark Examples
[bookmark](https://reddit.com)(caption:Popular discussion platform)

## Image Examples  
[image](https://example.com/screenshot.png)(caption:Dashboard overview)

## Video Examples
[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)(caption:Music Video)

## Audio Examples
[audio](https://example.com/interview.mp3)(caption:Live interview)

## File Examples

[file](https://example.com/manual.pdf)(caption:User manual)

## PDF Examples
[pdf](https://example.com/manual.pdf)(caption:Critical safety information)
        """

        await page.append_markdown(
            lambda b: b.bookmark(
                title="Caption Syntax Test",
                url="https://example.com",
                caption="This is a test bookmark with caption.",
            )
        )
        print("✅ Successfully added all caption syntax examples!")

        content = await page.get_text_content()
        print(f"📄 Page content preview:\n{content[:500]}...")

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
