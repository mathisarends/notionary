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

        # Test all media blocks with the MarkdownBuilder
        await page.append_markdown(
            lambda b: (
                b.h1("Caption Syntax Test")
                .h2("Media Block Examples")
                .bookmark(
                    url="https://reddit.com",
                    title="Reddit",
                    caption="Popular discussion platform"
                )
                .image(
                    url="https://example.com/screenshot.png",
                    caption="Dashboard overview"
                )
                .video(
                    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    caption="Music Video"
                )
                .audio(
                    url="https://example.com/interview.mp3",
                    caption="Live interview"
                )
                .file(
                    url="https://example.com/manual.pdf",
                    caption="User manual"
                )
                .pdf(
                    url="https://example.com/manual.pdf",
                    caption="Critical safety information"
                )
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
