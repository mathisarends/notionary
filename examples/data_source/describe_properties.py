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

        schema = data_source.describe_properties()
        print("Properties:")
        for name, info in schema.items():
            line = f"  - {name} [{info['type']}]"

            if "options" in info:
                options = ", ".join(info["options"])
                line += f" (options: {options})"

            if "groups" in info:
                groups = ", ".join(info["groups"])
                line += f" (groups: {groups})"

            if "format" in info:
                line += f" (format: {info['format']})"

            print(line)


if __name__ == "__main__":
    asyncio.run(main())
