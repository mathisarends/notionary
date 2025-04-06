"""
# Notion Database Writer Example
====================================

This script demonstrates how to use `DatabaseWritter` to automatically inspect
a Notion database schema—including relation discovery—and create or update
entries with correctly structured properties.
"""

import asyncio
from datetime import datetime

from notionary.core.database.notion_database_manager import NotionDatabaseSchema
from notionary.core.database.notion_database_writer import DatabaseWritter
from notionary.core.notion_client import NotionClient


async def main():
    """Creates and updates an entry in a Notion database based on schema inspection."""
    client = NotionClient()

    try:
        database_id = "1a6389d5-7bd3-8097-aa38-e93cb052615a"

        db_schema = NotionDatabaseSchema(database_id, client)
        if not await db_schema.load():
            print(f"❌ Could not load schema for database {database_id}")
            return

        property_types = await db_schema.get_property_types()
        print("📊 Database property types:")
        for name, prop_type in property_types.items():
            print(f"  • {name}: {prop_type}")

        db_writer = DatabaseWritter(client, db_schema)

        properties = {}
        relations = {}

        for name, prop_type in property_types.items():
            if prop_type == "title":
                properties[name] = "Automatically created entry"

            elif prop_type == "rich_text":
                properties[name] = "This is an example rich text."
            elif prop_type == "number":
                properties[name] = 42
            elif prop_type == "select":
                options = await db_schema.get_select_options(name)
                if options:
                    properties[name] = options[0].get("name")
            elif prop_type == "multi_select":
                options = await db_schema.get_select_options(name)
                if options and len(options) >= 2:
                    properties[name] = [options[0].get("name"), options[1].get("name")]
                elif options:
                    properties[name] = [options[0].get("name")]
            elif prop_type == "checkbox":
                properties[name] = True
            elif prop_type == "url":
                properties[name] = "https://example.com"
            elif prop_type == "date":
                # Current date
                today = datetime.now().strftime("%Y-%m-%d")
                properties[name] = {"start": today}
            elif prop_type == "relation":
                # Fetch relation options
                relation_options = await db_schema.get_relation_options(name, limit=2)
                if relation_options:
                    relations[name] = [option["title"] for option in relation_options]

        print("\n✨ Creating new database entry with the following properties:")
        for name, value in properties.items():
            print(f"  • {name}: {value}")

        if relations:
            print("\n🔗 Using the following relations:")
            for name, values in relations.items():
                print(f"  • {name}: {values}")

        # Create the page
        new_page = await db_writer.create_page(
            database_id=database_id, properties=properties, relations=relations
        )

        if new_page:
            page_id = new_page.get("id")
            page_url = new_page.get("url", "no URL available")
            print(f"\n✅ Entry successfully created with ID: {page_id}")
            print(f"   URL: {page_url}")
        else:
            print("\n❌ Failed to create the entry")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
