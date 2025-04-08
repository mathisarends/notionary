"""
# Notionary: Database Factory Example
=========================================

This example demonstrates how to use the NotionDatabaseFactory to connect to Notion databases
either by their ID or by name with fuzzy matching.
"""

import asyncio

from notionary.core.database.notion_database_manager_factory import (
    NotionDatabaseFactory,
)
from notionary.exceptions.database_exceptions import (
    DatabaseNotFoundException,
    DatabaseConnectionError,
)


async def main():
    """Demonstrate the NotionDatabaseFactory functionality."""
    print("🚀 Notionary Database Factory Example")

    print("\n🔍 Connecting to database by ID...")
    try:
        database_id = "1af389d5-7bd3-815c-937a-e0e39eb6343a"

        db_manager = await NotionDatabaseFactory.from_database_id(database_id)

        print(f"✅ Successfully connected to database: {db_manager.title}")
        print(f"🆔 Database ID: {db_manager.database_id}")

        # Clean up resources
        await db_manager.close()

    except DatabaseConnectionError as e:
        print(f"❌ Error connecting to database: {e}")

    # Example 2: Connect by name with fuzzy matching
    print("\n🔍 Searching for database by name...")

    try:
        # The factory will find the closest match to this name
        database_name = "Projects"

        # Use the factory to find and create a database manager by name
        db_manager = await NotionDatabaseFactory.from_database_name(database_name)

        print(f"✅ Found matching database: '{db_manager.title}'")
        print(f"🆔 Database ID: {db_manager.database_id}")

        # Clean up resources
        await db_manager.close()

    except DatabaseNotFoundException as e:
        print(f"❌ Database not found: {e}")
    except DatabaseConnectionError as e:
        print(f"❌ Error connecting to database: {e}")


if __name__ == "__main__":
    asyncio.run(main())
