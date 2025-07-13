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

from notionary import NotionDatabase

YOUR_DATABASE_NAME = "WISSEN/NOTIZEN"


async def main():
    db_manager: NotionDatabase = await NotionDatabase.from_database_name(
        database_name=YOUR_DATABASE_NAME
    )

    print("Seiten, die in den letzten 24 Stunden bearbeitet wurden:")
    count = 0
    async for page in db_manager.iter_pages_updated_within(hours=24):
        count += 1
        title, url, icon = await asyncio.gather(
            page.get_title(), page.get_url(), page.get_icon()
        )
        print(f"{count:2d}. {icon} {title}")
        print(f"    └─ {url}")


async def elegant_example():
    db = await NotionDatabase.from_database_name(YOUR_DATABASE_NAME)

    # Method-Chaining direkt auf Database
    async for page in db.iter_pages_with_filter(
        db.create_filter()
        .with_created_last_n_days(3)
        .with_status_equals("Status", "Entwurf")
    ):
        title = await page.get_title()
        print(f"John's recent task: {title}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(elegant_example())
