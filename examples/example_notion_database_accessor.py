"""
# Notionary: Database Discovery Example
=========================================

This example demonstrates how to use the NotionDatabaseAccessor to discover
and explore databases available in your Notion workspace. The example shows how to:

## Features
- Connect to the Notion API using your integration token
- List all databases available to your integration
- Display detailed information about each database
- Extract database titles and property schemas
"""

import asyncio
from typing import Dict, Any
from notionary.core.database.notion_database_schema import NotionDatabaseAccessor

async def print_database_details(
    database: Dict[str, Any], accessor: NotionDatabaseAccessor
) -> None:
    """Pretty print details of a single database."""

    db_id = database.get("id", "Unknown ID")
    title = accessor.extract_database_title(database)

    print(f"\n📚 Database: {title}")
    print(f"🆔 ID: {db_id}")

    if "properties" in database:
        print("\n🔑 Properties:")
        for prop_name, prop_details in database["properties"].items():
            prop_type = prop_details.get("type", "unknown")
            print(f"  • {prop_name} ({prop_type})")

    if "parent" in database:
        parent_type = database["parent"].get("type", "unknown")
        if parent_type == "page":
            parent_id = database["parent"].get("page_id", "unknown")
            print(f"\n📄 Parent: Page ({parent_id})")
        elif parent_type == "workspace":
            print("\n🏢 Parent: Workspace (top-level)")

    created_time = database.get("created_time", "Unknown")
    url = database.get("url", "No URL available")

    print(f"\n🕒 Created: {created_time}")
    print(f"🔗 URL: {url}")

    print("\n" + "=" * 50)


async def main():
    """Discover and explore databases in your Notion workspace."""

    print("🔑 Connecting to Notion API...")
    database_accessor = NotionDatabaseAccessor()

    print("🔍 Discovering databases...")

    db_count = 0

    async for database in database_accessor.iter_databases():
        db_count += 1
        await print_database_details(database, database_accessor)

        db_id = database.get("id")

        if not db_id:
            continue

    if db_count == 0:
        print(
            "\n⚠️ No databases found. Make sure your integration has access to databases."
        )
        print("Check that you've shared databases with your integration in Notion.")
    else:
        print(f"\n✅ Found {db_count} database(s) in your Notion workspace.")


if __name__ == "__main__":
    print("🚀 Starting Notion Database Discovery...")
    asyncio.run(main())
