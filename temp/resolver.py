import os
import asyncio

from notionary.blocks.rich_text.name_to_id_resolver import NameIdResolver


async def main():

    resolver = NameIdResolver()

    # Test data
    page_id = "1a3389d57bd380d7a507e67d1b25822c"
    page_name = "Jarvis Clipboard"

    database_id = "1a6389d5-7bd3-80a3-a60e-cb6bc02f85d6"
    database_name = "Wissen & Notizen"

    print("=== Testing Page and Database Resolution ===\n")

    # Resolve name -> ID
    resolved_id = await resolver.resolve_id(page_name)
    print(f"Resolved ID for name '{page_name}': {resolved_id}")

    # Resolve ID -> name
    resolved_name = await resolver.resolve_name(page_id)
    print(f"Resolved name for ID '{page_id}': {resolved_name}")

    print()

    # Resolve database name -> ID
    resolved_db_id = await resolver.resolve_id(database_name)
    print(f"Resolved ID for database name '{database_name}': {resolved_db_id}")

    # Resolve database ID -> name
    resolved_db_name = await resolver.resolve_name(database_id)
    print(f"Resolved name for database ID '{database_id}': {resolved_db_name}")


if __name__ == "__main__":
    asyncio.run(main())
