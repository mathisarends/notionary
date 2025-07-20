"""
# Notionary: Toggle Element Markdown Demo
========================================

A demo showing how to add custom toggle elements to Notion pages using Markdown.
Perfect for demonstrating ToggleElement syntax with pipe-prefixed content!

SETUP: Replace PAGE_NAME with an existing page in your Notion workspace.
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Demo of adding ToggleElement markdown to a Notion page."""

    print("🚀 Notionary Toggle Element Demo")
    print("=" * 35)

    try:
        print(f"🔍 Loading page: '{PAGE_NAME}'")
        page = await NotionPage.from_page_name(PAGE_NAME)
        
        print(f"\n{page.emoji_icon} Page Information:")
        print(f"├── Title: {page.title}")
        print(f"├── ID: {page.id}")
        print(f"└── Visit at: {page.url}")
        
        toggle_content = """
        ## 🔽 Toggle Element Examples

        +++ Key Findings
        | The research demonstrates **three main conclusions**:
        | 1. First important point about user behavior
        | 2. Second important point about performance metrics
        | 3. Third important point about future implications
        """
        
        # Add the markdown content to the page
        print("\n📝 Adding Toggle Element examples...")
        await page.append_markdown(toggle_content)
        
        print(f"\n✅ Successfully added toggle examples to '{page.title}'!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the page name exists in your Notion workspace")


if __name__ == "__main__":
    asyncio.run(main())