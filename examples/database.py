"""
# Notionary: Database Demo
=========================

A quick demo showing basic database information retrieval and operations.
Perfect for getting started with Notionary databases!

SETUP: Replace DATABASE_NAME with an existing database in your Notion workspace.
"""

import asyncio
import traceback
from notionary import NotionDatabase

# REPLACE DATABASE NAME
DATABASE_NAME = "Wissen/Notizen"

async def main():
    """Simple demo of NotionDatabase basic operations."""

    print("🚀 Notionary Database Demo")
    print("=" * 30)

    try:
        print(f"🔍 Loading database: '{DATABASE_NAME}'")
        db = await NotionDatabase.from_database_name(DATABASE_NAME)
        
        # Display basic database information
        print(f"\n{db.emoji} Database Information:")
        print(f"├── Title: {db.title}")
        print(f"├── ID: {db.id}")
        print(f"└── Visit at: {db.url}")
        
        print("\n📄 Creating a new page...")
        page = await db.create_blank_page()

        await page.set_title("Notionary Demo Page")
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

        print(f"✅ Page created in database '{db.title}' (ID: {db.from_database_id})")
        print(f"├── Page title: {page.title}")
        print(f"├── Page emoji: {page.emoji_icon}")
        print(f"└── Visit at: {page.url}")
        

    except Exception as e:
        print("❌ Error: {}".format(e))
        print("🔍 Full traceback:\n{}".format(traceback.format_exc()))
        print("💡 Make sure the database name exists in your Notion workspace \n")


if __name__ == "__main__":
    asyncio.run(main())