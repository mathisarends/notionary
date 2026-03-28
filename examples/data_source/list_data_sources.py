"""List all data sources in the workspace."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        data_sources = await notion.data_sources.list()
        for ds in data_sources:
            print(f"{ds.title} ({ds.url})")


if __name__ == "__main__":
    asyncio.run(main())
