"""
# Notionary: Clean Database to Page Example
=========================================

This example demonstrates a clean workflow connecting to a Notion database
and creating a new page with title, icon, and content.

IMPORTANT: Replace DATABASE_NAME with the name of your actual Notion database.
The factory will use fuzzy matching to find the closest match to this name.
"""

import asyncio
import textwrap

from notionary import NotionDatabaseFactory
from notionary.exceptions.database_exceptions import DatabaseNotFoundException

DATABASE_NAME = "WISSEN/NOTIZEN"  # YOUR_DATABASE_NAME_HERE


async def main():
    """Demonstrate a simple Notion database to page workflow."""
    print("✨ Notionary Simple Workflow Example")
    print("===================================")

    try:
        print("\n🔎 Connecting to database by name...")

        db_manager = await NotionDatabaseFactory.from_database_name(DATABASE_NAME)

        page_manager = await db_manager.create_blank_page()

        print("📝 Setting page properties...")

        await page_manager.set_title("Notionary Demo Example Page")
        await page_manager.set_page_icon("🌟")
        await page_manager.set_random_gradient_cover()

        print("🎨 Page styled with title, icon and cover")

        print("📄 Adding content to the page...")

        content = textwrap.dedent(
            """
        # Notionary API Demo

        This page was created using the Notionary API through an automated example.

        ## Key Steps
        - Connect to database using NotionDatabaseFactory
        - Create a new page in the database
        - Use NotionPageManager to set properties and add content

        ## Features Demonstrated
        - Database connection by name (fuzzy matching)
        - Page creation
        - Setting page title
        - Adding an emoji icon
        - Setting a random gradient cover
        - Appending markdown content
        """
        )

        await page_manager.append_markdown(content)
        print("📋 Content added successfully")

    except DatabaseNotFoundException as e:
        print(f"❌ Database not found: {e}")


if __name__ == "__main__":
    print("🚀 Starting Notionary example...")
    asyncio.run(main())
    print("✅ Example completed!")
