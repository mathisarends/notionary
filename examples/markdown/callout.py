"""
# Notionary: Callout Element Markdown Demo
==========================================

A demo showing how to add custom callout elements to Notion pages using Markdown.
Perfect for demonstrating CalloutElement syntax!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Demo of adding CalloutElement markdown to a Notion page."""

    print("🚀 Notionary Callout Element Demo")
    print("=" * 36)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)

        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"├── ID: {page.id}")
        print(f"└── Visit at: {page.url}")

        callout_content = """
        ## 📢 Callout Element Examples

        !> [💡] This is a default callout with the light bulb emoji

        !> [🔔] This is a callout with a bell emoji

        !> [⚠️] Warning: This is an important note to pay attention to

        !> [💡] Tip: Add emoji that matches your content's purpose

        !> [✅] Success: Your operation completed successfully

        !> [🚨] Critical: Immediate action required
        """

        # Add the markdown content to the page
        print("\n📝 Adding Callout Element examples...")
        await page.append_markdown(callout_content)

        print(f"\n✅ Successfully added callout examples to '{page.title}'!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())
