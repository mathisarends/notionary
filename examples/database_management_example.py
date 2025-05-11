"""
# Notionary: Database Management Example
======================================

This example demonstrates how to find and work with Notion databases,
including discovery, filtering pages, and creating new content.

IMPORTANT: Replace DATABASE_NAME with the name of your actual Notion database.
The factory will use fuzzy matching to find the closest match to this name.
"""

import asyncio
from notionary import NotionDatabase

DATABASE_NAME = "WISSEN/NOTIZEN"


async def main():
    """Demonstrate database operations with Notionary."""
    print("🗄️ Notionary Database Example")
    print("============================")

    try:
        print(f"\n🔎 Connecting to database '{DATABASE_NAME}'...")
        db = await NotionDatabase.from_database_name(DATABASE_NAME)

        print("📄 Creating a new page...")
        page = await db.create_blank_page()

        await page.set_title("Notionary")
        await page.set_emoji_icon("🚀")
        await page.set_random_gradient_cover()

        # Add markdown content
        content = """
        !> [🎯] Welcome to Notionary! The easiest way to automate Notion with Python

        ## Why Choose Notionary?

        1. **Simple API** - Connect to databases and pages with just `one line of code`
        2. **Extended Markdown** - Use Notion-specific elements like *callouts*, *toggles*, and *embeds*
        3. **Async Support** - Built for modern Python with full `async/await` support
        4. **Smart Features** - *Fuzzy search*, *batch processing*, and *automatic retries*
        5. **Type Safety** - Full type hints for better IDE support

        ---

        ## ⚡ Quick Start Examples

        ```python
        from notionary import NotionDatabase

        # Find database by name (fuzzy matching)
        db = await NotionDatabase.from_database_name("Projects")

        # Create a new page
        page = await db.create_blank_page()
        await page.set_title("New Project")
        ```
        Caption: Connect to a Notion database and create a page
        
        ```python
        from notionary import NotionPage

        # Find page by name
        page = await NotionPage.from_page_name("Meeting Notes")

        # Update content
        await page.append_markdown("## Action Items\\n- [ ] Follow up with team")

        # Set properties
        await page.set_property_value_by_name("Status", "In Progress")
        ```
        Caption: Update content and properties on an existing page

        Built with ❤️ for the Notion community."""
        await page.append_markdown(content)

        print(f"✅ Page created: {await page.get_url()}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Starting Notionary database example...")
    asyncio.run(main())
    print("✅ Example completed!")
