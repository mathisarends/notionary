"""
# Notionary: Page Management Example
===================================

This example demonstrates how to find and display Notion page information
using only getter methods (no modifications).

IMPORTANT: Replace PAGE_NAME with the name of an existing Notion page.
"""

import asyncio
from notionary import NotionPage

PAGE_NAME = "Simplex Algorithmus für das Leben"


async def main():
    """Demonstrate page getters with Notionary."""
    print("📄 Notionary Page Example (Getters Only)")
    print("========================")

    try:
        print(f"\n🔎 Finding page '{PAGE_NAME}'...")
        page = await NotionPage.from_page_name(PAGE_NAME)
        updated_property_value = await page.set_property_value_by_name(
            "Projekte", ["Hueify"]
        )
        print("updated_property_value", updated_property_value)

    except Exception as e:
        import traceback

        print(f"❌ Error: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    print("🚀 Starting Notionary page example...")
    asyncio.run(main())
    print("✅ Example completed!")
