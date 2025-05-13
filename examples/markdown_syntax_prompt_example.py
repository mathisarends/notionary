"""
# Notionary: Page Management Example
===================================

This example demonstrates how to find and modify Notion pages,
including content updates, property changes, and formatting.

IMPORTANT: Replace PAGE_NAME with the name of an existing Notion page.
The factory will use fuzzy matching to find the closest match to this name.
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


# TODO: Build the prompts for that here and evaluate outcomes.
# Export prompting module so nobody has to "merk sich stuff"
async def main():
    """Demonstrate page operations with Notionary."""
    print("📄 Notionary Page Example")
    print("========================")

    try:
        print(f"\n🔎 Finding page '{PAGE_NAME}'...")
        page = await NotionPage.from_page_name(PAGE_NAME)

        system_prompt = page.get_notion_markdown_system_prompt()
        print(f"System prompt: {system_prompt}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Starting Notionary page example...")
    asyncio.run(main())
    print("✅ Example completed!")
