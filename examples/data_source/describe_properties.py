"""Inspect a data source property schema for agent-friendly context."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        data_source = await notion.data_sources.find("Projekte")

        print(f"Data source: {data_source.title}")
        print(f"URL: {data_source.url}\n")

        schema = await data_source.describe_properties(limit=50)
        print("schema", schema)


if __name__ == "__main__":
    asyncio.run(main())
