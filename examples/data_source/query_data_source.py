import asyncio

from dotenv import load_dotenv

from notionary import Notionary
from notionary.data_source.query import (
    Filter,
    PropertySort,
    SortDirection,
    TimestampSort,
)

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        ds = await notion.data_sources.find("Projekte")
        print(f"Data source: {ds.title}\n")

        all_pages = await ds.query(limit=5)
        print(f"All pages (first 5): {[p.title for p in all_pages]}\n")

        active = await ds.query(filter=Filter.status("Status").equals("In Bearbeitung"))
        print(f"In Progress: {[p.title for p in active]}\n")

        sorted_pages = await ds.query(
            sorts=[
                PropertySort(property="Name", direction=SortDirection.ASCENDING),
            ],
            limit=10,
        )
        print(f"Sorted by name: {[p.title for p in sorted_pages]}\n")

        print("Streaming all pages:")
        async for page in ds.iter_query(
            sorts=[
                TimestampSort(
                    timestamp="last_edited_time",
                    direction=SortDirection.DESCENDING,
                )
            ],
            limit=10,
        ):
            print(f"  - {page.title}")


if __name__ == "__main__":
    asyncio.run(main())
