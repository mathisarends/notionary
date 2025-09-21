"""
# Notionary: Audio Element Markdown Demo
=======================================

A demo showing how to add custom audio elements to Notion pages using Markdown.
Perfect for demonstrating AudioElement syntax!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio

from notionary import MarkdownBuilder, NotionPage

PAGE_NAME = "Jarvis Clipboard"


def create_audio_examples() -> str:
    """Creates comprehensive audio examples using MarkdownBuilder."""
    return (
        MarkdownBuilder()
        .h2("🎵 Audio Elements")
        .paragraph("Audio elements let you embed audio files directly in your Notion pages.")
        .space()
        .audio(
            url="https://storage.googleapis.com/audio_summaries/ep_ai_summary_127d02ec-ca12-4312-a5ed-cb14b185480c.mp3",
            caption="AI in Healthcare: A comprehensive discussion on the impact of artificial intelligence in modern healthcare systems.",
        )
        .space()
        .callout(
            text="Audio elements support most common audio formats and automatically display playback controls in Notion!",
            emoji="🎧",
        )
        .build()
    )


async def main():
    """Demo of adding audio elements to a Notion page."""

    print("🚀 Notionary Audio Element Demo")
    print("=" * 33)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"└── URL: {page.url}")

        print("\n🎵 Creating audio examples...")
        content = create_audio_examples()

        print("✨ Adding content to page...")
        await page.append_markdown(content)

        print("\n✅ Successfully added audio examples!")
        print(f"🌐 View at: {page.url}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
