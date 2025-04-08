"""
# Notionary: Simple Database Page Listing
=========================================

This example demonstrates how to use the Notion API to list all pages in a database.
It uses `NotionDatabaseSchema` to efficiently iterate over pages without loading them all into memory.

## Features
- Connect to a Notion database via its ID
- Apply optional filters to fetch specific pages (e.g. status)
- Efficiently iterate over database pages using async generators
- Extract and print basic metadata such as page titles and IDs
"""

from notionary.core.database.notion_database_schema import NotionDatabaseSchema
from notionary.core.notion_client import NotionClient
from notionary.core.page.notion_page_manager import NotionPageManager


async def list_all_pages(schema: NotionDatabaseSchema) -> None:
    """Lists all pages in the Notion database without any filters."""
    print("All Pages")
    print("-" * 50)

    count = 0
    page: NotionPageManager
    async for page in schema.iter_database_pages():
        page_id = page.page_id
        title = page.title or "Untitled Page"
        print(f"{page_id[:8]}... | {title}")
        count += 1

    print("-" * 50)
    print(f"Total of {count} entries found")


async def list_filtered_pages(schema: NotionDatabaseSchema) -> None:
    """Lists only pages in the Notion database with status 'In Bearbeitung'."""
    filter_conditions = {"property": "Status", "status": {"equals": "In Bearbeitung"}}

    print("Filtered Pages (Status: In Bearbeitung)")
    print("-" * 50)

    count = 0
    async for page in schema.iter_database_pages(filter_conditions=filter_conditions):
        page_id = page.page_id
        title = page.title(page)
        print(f"{page_id[:8]}... | {title}")
        count += 1

    print("-" * 50)
    print(f"Total of {count} entries found")


async def main() -> None:
    client = NotionClient()
    try:
        database_id = "1af389d5-7bd3-815c-937a-e0e39eb6343a"
        schema = NotionDatabaseSchema(database_id, client)

        await list_all_pages(schema)
        await list_filtered_pages(schema)

    finally:
        await client.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
