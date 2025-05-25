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


async def main():
    """Demonstrate page operations with Notionary."""
    print("📄 Notionary Page Example")
    print("========================")

    try:
        print(f"\n🔎 Finding page '{PAGE_NAME}'...")
        page = await NotionPage.from_page_name(PAGE_NAME)

        print("✨ Updating page properties...")

        prompt = page.get_notion_markdown_system_prompt()
        print(f"📝 System Prompt:\n{prompt}\n")
        
        markdown = """        
!> [📝] Key insight: Understanding the critical components of a successful SaaS engineering concept requires focusing on both market validation and technical structuring.

- Proven Market Value: Ensure there is a demand and willingness to pay.
- **Focus on UI First:** Prioritize user interface development.
- Supabase: Supports MCP with cursor functionality.
- Implement effective cursor rules for efficient operation.

### 🚀 Schrittweise
- **UI:** Begin with user interface design.
- **Datamodell:** Develop a robust data model.
- **Connect:** Establish necessary connections and integrations.
- **Polish:** Refine and enhance the application.
"""
        
        await page.append_markdown(markdown, append_divider=True)

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Starting Notionary page example...")
    asyncio.run(main())
    print("✅ Example completed!")
