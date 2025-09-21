"""
# Notionary: Updated Pages Iterator Example
==========================================

This example demonstrates how to iterate through pages updated in the last 7 days in a Notion database.

IMPORTANT: Replace YOUR_DATABASE_NAME with the name of your actual Notion database.
The factory will use fuzzy matching to find the closest match to this name.
"""

from notionary import NotionDatabase

YOUR_DATABASE_NAME = "WISSEN/NOTIZEN"


async def main():
    db = await NotionDatabase.from_database_name(YOUR_DATABASE_NAME)

    print("Pages updated in the last 7 days:")
    count = 0
    async for page in db.iter_pages_updated_within(hours=168):  # 7 days = 168 hours
        count += 1
        print(f"{count:2d}. {page.emoji_icon if page.emoji_icon else ''} {page.title}")
        print(f"    └─ {page.url}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
