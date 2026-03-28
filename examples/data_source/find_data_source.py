"""Find a data source by title and inspect its properties."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        ds = await notion.data_sources.from_title("Projects")

        print(f"Title: {ds.title}")
        print(f"URL:   {ds.url}")
        print(f"Properties: {list(ds.properties.keys())}")


if __name__ == "__main__":
    asyncio.run(main())
