"""
Finds a Notion data source (e.g., database or collection) by its title and lists a few pages from it.
"""

import asyncio

from notionary import NotionDataSource

# Replace with your datasource/database title
DATA_SOURCE_TITLE = "Inbox"


async def main() -> None:
    data_source = await NotionDataSource.from_title(DATA_SOURCE_TITLE)
    print(f"Found datasource: {data_source.title} (URL: {data_source.url})")

    query = data_source.filter().order_by_last_edited_time_descending().limit(5).build()

    async for page in data_source.get_pages_stream(query):
        print(f"- {page.title} (URL: {page.url})")


if __name__ == "__main__":
    asyncio.run(main())
