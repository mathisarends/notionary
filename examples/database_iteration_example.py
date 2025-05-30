"""
# Notionary: Recent Pages Iterator Example
==========================================

This example demonstrates how to iterate through pages created within
the last 24 hours in a Notion database, filtering out specific conditions.

IMPORTANT: Replace YOUR_DATABASE_NAME with the name of your actual Notion database.
The factory will use fuzzy matching to find the closest match to this name.

The filter is generic and only uses the created_time property which exists
on all Notion pages. You can customize the filter conditions based on your
specific database properties.
"""

from datetime import datetime, timedelta
from notionary import NotionDatabase

YOUR_DATABASE_NAME = "WISSEN/NOTIZEN"


async def main():
    db_manager: NotionDatabase = await NotionDatabase.from_database_name(
        database_name=YOUR_DATABASE_NAME
    )

    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

    filter_conditions = {
        "timestamp": "created_time",
        "created_time": {"after": twenty_four_hours_ago.isoformat()},
    }

    count = 0
    async for page in db_manager.iter_pages(filter_conditions=filter_conditions):
        count += 1
        title, url, icon = await asyncio.gather(
            page.get_title(), page.get_url(), page.get_icon()
        )

        print(f"{count:2d}. {icon} {title}")
        print(f"    └─ {url}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
