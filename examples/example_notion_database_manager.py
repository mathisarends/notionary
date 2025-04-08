import asyncio
import traceback
from datetime import datetime

from notionary.core.database.notion_database_manager import NotionDatabaseManager


async def main():
    """Demonstrates the usage of the NotionDatabaseFacade."""
    database_id = "1a6389d5-7bd3-8097-aa38-e93cb052615a"
    db = NotionDatabaseManager(database_id)

    try:
        if not await db.initialize():
            print("❌ Failed to initialize database")
            return

        db_name = await db.get_database_name()
        print(f"📊 Working with database: {db_name}")

        # Get property types
        property_types = await db.get_property_types()
        print("\n⚙️ Database properties:")
        for name, prop_type in property_types.items():
            print(f"  • {name}: {prop_type}")

        # Prepare properties and relations for a new page
        properties = {}
        relations = {}

        # Dynamically build properties based on database schema
        for name, prop_type in property_types.items():
            if prop_type == "title":
                properties[name] = "Created via Notionary"
            elif prop_type == "rich_text":
                properties[name] = "This entry was created using Notionary."
            elif prop_type == "number":
                properties[name] = 42
            elif prop_type == "select":
                options = await db.get_select_options(name)
                if options:
                    properties[name] = options[0]["name"]
            elif prop_type == "multi_select":
                options = await db.get_select_options(name)
                if options and len(options) >= 2:
                    properties[name] = [options[0]["name"], options[1]["name"]]
                elif options:
                    properties[name] = [options[0]["name"]]
            elif prop_type == "checkbox":
                properties[name] = True
            elif prop_type == "url":
                properties[name] = "https://example.com"
            elif prop_type == "date":
                today = datetime.now().strftime("%Y-%m-%d")
                properties[name] = {"start": today}
            elif prop_type == "relation":
                relation_options = await db.get_relation_options(name, limit=2)
                if relation_options:
                    relations[name] = [option["title"] for option in relation_options]

        print("\n✨ Creating new page...")
        result = await db.create_page(properties, relations)

        # Check if creation was successful
        if result["success"]:
            page_id = result["page_id"]
            url = result.get("url", "No URL available")
            print("✅ Page created successfully!")
            print(f"  • ID: {page_id}")
            print(f"  • URL: {url}")

            # Update the created page
            print("\n🔄 Updating page...")
            update_properties = {}
            for name, prop_type in property_types.items():
                if prop_type == "title":
                    update_properties[name] = "Updated via Database Facade"
                elif prop_type == "rich_text":
                    update_properties[name] = (
                        "This entry was updated using NotionDatabaseFacade."
                    )

            update_result = await db.update_page(page_id, update_properties)
            if update_result["success"]:
                print("✅ Page updated successfully!")
            else:
                print(f"❌ Failed to update page: {update_result.get('message')}")

            # Get page as NotionPageManager
            print("\n📄 Getting page manager...")
            page_manager = await db.get_page_manager(page_id)
            if page_manager:
                print(f"✅ Got page manager with title: {page_manager.title}")

                print("\n📝 Appending content...")
                await page_manager.append_markdown(
                    """
# This is a heading
This content was appended using the NotionPageManager.

## Features
- Easy to use
- High-level API
- Handles relations
                """
                )
                print("✅ Content added successfully!")

            # List pages in the database
            print("\n📋 Listing pages in database (max 5)...")
            pages = await db.get_pages(limit=5)
            print(f"Found {len(pages)} pages:")
            for i, page in enumerate(pages, 1):
                print(f"  {i}. {page.title} ({page.page_id})")

            # Optional: Delete the created page
            if input("\n❓ Delete the created page? (y/n): ").lower() == "y":
                delete_result = await db.delete_page(page_id)
                if delete_result["success"]:
                    print("✅ Page deleted successfully!")
                else:
                    print(f"❌ Failed to delete page: {delete_result.get('message')}")

        else:
            print(f"❌ Failed to create page: {result.get('message')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()

    finally:
        # Close the client connection
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
