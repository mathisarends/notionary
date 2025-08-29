"""
# Notionary: Embed Element Demo
==============================

Simple demo showing how to embed external content using MarkdownBuilder.
Perfect for adding YouTube videos, maps, and other embeddable content!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio

from notionary import MarkdownBuilder, NotionPage

PAGE_NAME = "Jarvis Clipboard"


def create_embed_examples() -> str:
    """Creates embed examples using MarkdownBuilder."""
    return (
        MarkdownBuilder()
        .h2("🌐 Embed Elements")
        .paragraph("Embeds let you include external content directly in your Notion pages.")
        .space()
        
        .embed(
            url="https://www.youtube.com/watch?v=x7X9w_GIm1s&ab_channel=Fireship",
            caption="Python in 100 seconds - A lightning-fast Python tutorial by Fireship"
        )
        .space()
        
        .callout(
            text="Most popular platforms support embedding: YouTube, Twitter, GitHub, CodePen, Figma, and many more!",
            emoji="🔗"
        )
        .build()
    )


async def main():
    """Demo of adding embed elements to a Notion page."""
    
    print("🚀 Notionary Embed Element Demo")
    print("=" * 34)
    
    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)
        
        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"└── URL: {page.url}")
        
        print("\n🌐 Creating embed examples...")
        content = create_embed_examples()
        
        print("✨ Adding content to page...")
        await page.append_markdown(content)
        
        print("\n✅ Successfully added embed examples!")
        print(f"🌐 View at: {page.url}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
