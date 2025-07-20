"""
# Notionary: Audio Element Markdown Demo
=======================================

A demo showing how to add custom audio elements to Notion pages using Markdown.
Perfect for demonstrating AudioElement syntax!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Demo of adding AudioElement markdown to a Notion page."""

    print("🚀 Notionary Audio Element Demo")
    print("=" * 35)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)
        
        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"├── ID: {page.id}")
        print(f"└── Visit at: {page.url}")
        
        audio_content = """
        ## 🎵 Audio Element Examples

        $[AI in Healthcare - Episode 42](https://storage.googleapis.com/audio_summaries/ep_ai_summary_127d02ec-ca12-4312-a5ed-cb14b185480c.mp3)
        """
        
        # Add the markdown content to the page
        print("\n📝 Adding Audio Element examples...")
        await page.append_markdown(audio_content)
        
        print(f"\n✅ Successfully added audio examples to '{page.title}'!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())