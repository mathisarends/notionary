"""
# Notionary: Recent Pages Iterator Example
==========================================

This example demonstrates how to iterate through pages created in the last N days in a Notion database.

IMPORTANT: Replace YOUR_DATABASE_NAME with the name of your actual Notion database.
The factory will use fuzzy matching to find the closest match to this name.

The filter uses only the created_time property, which exists on all Notion pages. You can customize the filter conditions based on your specific database properties.
"""

from notionary import NotionDatabase

YOUR_DATABASE_NAME = "WISSEN/NOTIZEN"


async def elegant_example():
    db = await NotionDatabase.from_database_name(YOUR_DATABASE_NAME)

    print("Pages created in the last 3 days:")
    count = 0
    async for page in db.iter_pages_with_filter(
        db.create_filter().with_created_last_n_days(3)
    ):
        count += 1
        print(f"{count:2d}. {page.emoji_icon if page.emoji_icon else ""} {page.title}")
        print(f"    └─ {page.url}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(elegant_example())
