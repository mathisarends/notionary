"""
# Notionary: Embed Element Markdown Demo
=======================================

A demo showing how to add custom embed elements to Notion pages using Markdown.
Perfect for demonstrating EmbedElement syntax!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio

from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Demo of adding EmbedElement markdown to a Notion page."""

    print("🚀 Notionary Embed Element Demo")
    print("=" * 34)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"├── ID: {page.id}")
        print(f"└── Visit at: {page.url}")

        embed_content = """
        ## 🌐 YouTube Gallery

        [embed](https://www.youtube.com/watch?v=dQw4w9WgXcQ "Never gonna give you up")

        *Rick Astley's classic 'Rickroll' meme. If you click, you know what happens!*

        ---

        [embed](https://www.youtube.com/watch?v=OQSNhk5ICTI "Double Rainbow")

        *A viral video of pure joy and wonder at seeing a double rainbow. "What does it mean?"*

        ---

        [embed](https://www.youtube.com/watch?v=x7X9w_GIm1s&ab_channel=Fireship "Python in 100 seconds")

        *A lightning-fast Python tutorial by Fireship. Learn the basics, syntax, and core concepts of Python in just 100 seconds!*
        """

        # Add the markdown content to the page
        print("\n📝 Adding Embed Element examples...")
        await page.append_markdown(embed_content)

        print(f"\n✅ Successfully added embed examples to '{page.title}'!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
